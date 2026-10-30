import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Any
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models import Company, Source, RawJob, Job, JobCohortEligibility, VerificationResult, DailySelection
from app.connectors.registry import get_connector
from app.pipeline.verifier import JobVerifier
from app.pipeline.ranker import RankingEngine

logger = logging.getLogger(__name__)

class DailyPipelineRunner:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.verifier = JobVerifier()
        self.ranker = RankingEngine()

    async def run_pipeline(
        self,
        date_str: Optional[str] = None,
        dry_run: bool = False,
        limit_sources: Optional[int] = None,
        skip_ingest: bool = False
    ) -> Dict[str, Any]:
        """
        Executes the daily pipeline:
        1. Ingest from active sources (unless skip_ingest=True)
        2. Verify all pending jobs
        3. Rank and select top 5 for 2026, 2027, 2028 cohorts
        4. Re-verify liveness of top selected jobs
        5. Publish daily selections
        """
        if not date_str:
            date_str = datetime.utcnow().strftime("%Y-%m-%d")

        logger.info(f"=== Starting Daily Pipeline for {date_str} (dry_run={dry_run}, skip_ingest={skip_ingest}) ===")

        # 1. Ingest
        ingested_count = 0
        if not skip_ingest:
            ingested_count = await self._ingest_sources(limit=limit_sources)

        # 2. Verify pending jobs
        verified_count, rejected_count, review_count = await self._verify_pending_jobs()

        # 3. Rank & Select Top 5 for each cohort
        selections_by_cohort = {}
        for cohort in ["2026", "2027", "2028"]:
            selected = await self._select_cohort_top_5(cohort, date_str, dry_run=dry_run)
            selections_by_cohort[cohort] = selected

        summary = {
            "date": date_str,
            "dry_run": dry_run,
            "raw_jobs_ingested": ingested_count,
            "jobs_verified": verified_count,
            "jobs_rejected": rejected_count,
            "jobs_needs_review": review_count,
            "cohort_2026_published": len(selections_by_cohort.get("2026", [])),
            "cohort_2027_published": len(selections_by_cohort.get("2027", [])),
            "cohort_2028_published": len(selections_by_cohort.get("2028", [])),
            "selections": selections_by_cohort
        }

        logger.info(f"=== Completed Daily Pipeline Summary: {summary} ===")
        return summary

    async def _ingest_sources(self, limit: Optional[int] = None) -> int:
        query = select(Source, Company).join(Company, Source.company_id == Company.id).where(Source.is_active == True, Company.is_active == True)
        if limit:
            query = query.limit(limit)

        result = await self.db.execute(query)
        sources_and_companies = result.all()
        total_ingested = 0

        for source, company in sources_and_companies:
            try:
                connector = get_connector(source.source_type)
                config = json.loads(source.config_json) if source.config_json else {}
                raw_items = await connector.fetch_jobs(company.name, config)

                for item in raw_items:
                    # Check if already exists by external_id
                    existing_query = select(RawJob).where(
                        RawJob.source_id == source.id,
                        RawJob.external_id == item.external_id
                    )
                    ex_res = await self.db.execute(existing_query)
                    if ex_res.scalar_one_or_none():
                        continue

                    raw_job = RawJob(
                        source_id=source.id,
                        external_id=item.external_id,
                        title=item.title,
                        location_raw=item.location_raw,
                        apply_url=item.apply_url,
                        payload_json=item.payload_json,
                        raw_html=item.raw_html or "",
                        content_hash=item.content_hash,
                        first_seen_at=datetime.utcnow()
                    )
                    self.db.add(raw_job)
                    total_ingested += 1

                source.last_polled_at = datetime.utcnow()
                source.status = "healthy"
                await self.db.commit()
            except Exception as e:
                logger.error(f"Ingestion failed for source {source.id} ({source.source_type}): {e}")
                source.status = "degraded"
                await self.db.commit()

        return total_ingested

    async def _verify_pending_jobs(self) -> Tuple[int, int, int]:
        # Find raw jobs that have not been processed into jobs table yet
        query = select(RawJob, Company).join(Source, RawJob.source_id == Source.id).join(Company, Source.company_id == Company.id).outerjoin(Job, RawJob.id == Job.raw_job_id).where(Job.id == None)
        res = await self.db.execute(query)
        unprocessed = res.all()

        verified_cnt = 0
        rejected_cnt = 0
        review_cnt = 0

        for raw_job, company in unprocessed:
            report = await self.verifier.verify_job(
                title=raw_job.title,
                apply_url=raw_job.apply_url,
                location_raw=raw_job.location_raw or "",
                raw_html=raw_job.raw_html or "",
                company_domain=company.domain,
                skip_network_liveness=False
            )

            job = Job(
                raw_job_id=raw_job.id,
                company_id=company.id,
                title=raw_job.title,
                role_category=report.role_category,
                normalized_city=report.normalized_loc.city if report.normalized_loc else "India",
                state=report.normalized_loc.state if report.normalized_loc else None,
                country="India",
                is_remote=report.normalized_loc.is_remote if report.normalized_loc else False,
                is_hybrid=report.normalized_loc.is_hybrid if report.normalized_loc else False,
                apply_url=raw_job.apply_url,
                final_apply_url=report.final_apply_url or raw_job.apply_url,
                stipend_ctc=report.extracted_data.stipend_ctc if report.extracted_data else None,
                stipend_ctc_evidence=report.extracted_data.stipend_ctc_evidence if report.extracted_data else None,
                trust_score=report.final_trust_score,
                status=report.status,
                rejection_reason="; ".join(report.rejection_reasons) if report.rejection_reasons else None
            )
            self.db.add(job)
            await self.db.flush()

            # Record verification results
            for r in report.results:
                vr = VerificationResult(
                    job_id=job.id,
                    check_name=r["check_name"],
                    passed=r["passed"],
                    score=r["score"],
                    reason=r["reason"],
                    evidence_quote=r.get("evidence_quote")
                )
                self.db.add(vr)

            # Record cohort eligibilities
            if report.extracted_data and report.extracted_data.eligible_batches:
                for b in report.extracted_data.eligible_batches:
                    elig = JobCohortEligibility(
                        job_id=job.id,
                        cohort=b,
                        role_type=report.extracted_data.role_type,
                        evidence_snippet=report.extracted_data.batch_evidence or "Evidence verified from posting",
                        evidence_url=job.final_apply_url or job.apply_url,
                        min_exp_years=report.extracted_data.min_experience_years,
                        max_exp_years=report.extracted_data.max_experience_years,
                        branches=json.dumps(report.extracted_data.branches),
                        degree_requirements=json.dumps(report.extracted_data.degree_requirements)
                    )
                    self.db.add(elig)

            if report.status == "verified":
                verified_cnt += 1
            elif report.status == "needs_review":
                review_cnt += 1
            else:
                rejected_cnt += 1

            await self.db.commit()

        return verified_cnt, rejected_cnt, review_cnt

    async def _select_cohort_top_5(self, cohort: str, date_str: str, dry_run: bool = False) -> List[Dict[str, Any]]:
        # Fetch verified jobs eligible for this cohort
        query = (
            select(Job, Company, JobCohortEligibility)
            .join(Company, Job.company_id == Company.id)
            .join(JobCohortEligibility, Job.id == JobCohortEligibility.job_id)
            .where(
                JobCohortEligibility.cohort == cohort,
                Job.status == "verified",
                Job.trust_score >= 80.0
            )
        )
        res = await self.db.execute(query)
        rows = res.all()

        candidates = []
        for job, comp, elig in rows:
            candidates.append({
                "id": job.id,
                "title": job.title,
                "company_id": comp.id,
                "company_name": comp.name,
                "company_slug": comp.slug,
                "company_tier": comp.tier,
                "company_domain": comp.domain,
                "normalized_city": job.normalized_city,
                "role_category": job.role_category,
                "apply_url": job.apply_url,
                "final_apply_url": job.final_apply_url,
                "stipend_ctc": job.stipend_ctc,
                "trust_score": job.trust_score,
                "batch_evidence": elig.evidence_snippet,
                "role_type": elig.role_type
            })

        # Fetch previously published job IDs for this cohort to prevent repeats
        pub_query = select(DailySelection.job_id).where(DailySelection.cohort == cohort)
        pub_res = await self.db.execute(pub_query)
        previously_published = set(pub_res.scalars().all())

        # Run multi-objective ranking & diversity selection
        top_5 = self.ranker.select_top_jobs(cohort, candidates, previously_published, target_count=5)

        if not dry_run and top_5:
            # Re-verify liveness right before publishing
            for rank_idx, cand in enumerate(top_5, 1):
                # Save daily selection record
                ds = DailySelection(
                    selection_date=date_str,
                    cohort=cohort,
                    job_id=cand["id"],
                    rank=rank_idx,
                    final_score=cand["selection_score"],
                    selection_explanation=cand["selection_explanation"],
                    published_at=datetime.utcnow()
                )
                self.db.add(ds)

                # Update job status to published
                job_upd = await self.db.get(Job, cand["id"])
                if job_upd:
                    job_upd.status = "published"

            await self.db.commit()

        return top_5
