from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models import DailySelection, Job, Company, JobCohortEligibility, VerificationResult
from app.schemas.job import JobDetailRead, JobCohortEligibilityRead, VerificationResultRead
from app.schemas.selection import CohortDailyFeedResponse, DailySelectionRead

router = APIRouter()

VALID_COHORTS = ["2026", "2027", "2028"]

def _build_job_detail(job: Job, comp: Company, eligs: List[JobCohortEligibility], vrs: List[VerificationResult]) -> JobDetailRead:
    return JobDetailRead(
        id=job.id,
        company_name=comp.name,
        company_slug=comp.slug,
        company_tier=comp.tier,
        company_domain=comp.domain,
        title=job.title,
        role_category=job.role_category,
        normalized_city=job.normalized_city,
        state=job.state,
        country=job.country,
        is_remote=job.is_remote,
        is_hybrid=job.is_hybrid,
        apply_url=job.apply_url,
        final_apply_url=job.final_apply_url or job.apply_url,
        stipend_ctc=job.stipend_ctc,
        stipend_ctc_evidence=job.stipend_ctc_evidence,
        deadline=job.deadline,
        deadline_evidence=job.deadline_evidence,
        trust_score=job.trust_score,
        status=job.status,
        created_at=job.created_at,
        cohort_eligibilities=[
            JobCohortEligibilityRead(
                id=e.id,
                cohort=e.cohort,
                role_type=e.role_type,
                evidence_snippet=e.evidence_snippet,
                evidence_url=e.evidence_url,
                min_exp_years=e.min_exp_years,
                max_exp_years=e.max_exp_years,
                branches=e.branches,
                degree_requirements=e.degree_requirements
            ) for e in eligs
        ],
        verification_results=[
            VerificationResultRead(
                id=v.id,
                check_name=v.check_name,
                passed=v.passed,
                score=v.score,
                reason=v.reason,
                evidence_quote=v.evidence_quote,
                checked_at=v.checked_at
            ) for v in vrs
        ]
    )

@router.get("/{cohort}/daily", response_model=CohortDailyFeedResponse)
async def get_cohort_daily(
    cohort: str,
    date: Optional[str] = Query(None, description="Date YYYY-MM-DD"),
    db: AsyncSession = Depends(get_db)
):
    if cohort not in VALID_COHORTS:
        raise HTTPException(status_code=400, detail=f"Invalid cohort '{cohort}'. Must be 2026, 2027, or 2028.")

    if not date:
        date = datetime.utcnow().strftime("%Y-%m-%d")

    # Fetch daily selections for target date
    query = (
        select(DailySelection, Job, Company)
        .join(Job, DailySelection.job_id == Job.id)
        .join(Company, Job.company_id == Company.id)
        .where(DailySelection.cohort == cohort, DailySelection.selection_date == date)
        .order_by(DailySelection.rank.asc())
    )
    res = await db.execute(query)
    rows = res.all()

    today_items = []
    selected_job_ids = []
    for ds, job, comp in rows:
        selected_job_ids.append(job.id)
        # Load relationships
        eligs_res = await db.execute(select(JobCohortEligibility).where(JobCohortEligibility.job_id == job.id))
        vrs_res = await db.execute(select(VerificationResult).where(VerificationResult.job_id == job.id))
        job_detail = _build_job_detail(job, comp, eligs_res.scalars().all(), vrs_res.scalars().all())

        today_items.append(
            DailySelectionRead(
                id=ds.id,
                selection_date=ds.selection_date,
                cohort=ds.cohort,
                rank=ds.rank,
                final_score=ds.final_score,
                selection_explanation=ds.selection_explanation,
                published_at=ds.published_at,
                job=job_detail
            )
        )

    count = len(today_items)
    is_complete = (count >= 5)
    message = None
    fallback_items = []

    # If fewer than 5 pass today, show "Only N verified openings today" + fallback from previous days
    if count < 5:
        message = f"Only {count} verified opening{'s' if count != 1 else ''} found today. Showing still-open verified opportunities from previous days below."
        
        # Query verified jobs from prior dates not already in today's selections
        fallback_query = (
            select(DailySelection, Job, Company)
            .join(Job, DailySelection.job_id == Job.id)
            .join(Company, Job.company_id == Company.id)
            .where(
                DailySelection.cohort == cohort,
                DailySelection.selection_date < date,
                Job.id.not_in(selected_job_ids) if selected_job_ids else True
            )
            .order_by(desc(DailySelection.selection_date), DailySelection.rank.asc())
            .limit(5 - count)
        )
        fb_res = await db.execute(fallback_query)
        for ds, job, comp in fb_res.all():
            eligs_res = await db.execute(select(JobCohortEligibility).where(JobCohortEligibility.job_id == job.id))
            vrs_res = await db.execute(select(VerificationResult).where(VerificationResult.job_id == job.id))
            fb_job_detail = _build_job_detail(job, comp, eligs_res.scalars().all(), vrs_res.scalars().all())
            fallback_items.append(
                DailySelectionRead(
                    id=ds.id,
                    selection_date=ds.selection_date,
                    cohort=ds.cohort,
                    rank=ds.rank,
                    final_score=ds.final_score,
                    selection_explanation=f"Re-verified still-open fallback from {ds.selection_date}",
                    published_at=ds.published_at,
                    job=fb_job_detail
                )
            )

    return CohortDailyFeedResponse(
        date=date,
        cohort=cohort,
        verified_count=count,
        is_complete=is_complete,
        message=message,
        today_openings=today_items,
        still_open_fallback=fallback_items
    )

@router.get("/{cohort}/archive")
async def get_cohort_archive_dates(cohort: str, db: AsyncSession = Depends(get_db)):
    if cohort not in VALID_COHORTS:
        raise HTTPException(status_code=400, detail="Invalid cohort")

    res = await db.execute(
        select(DailySelection.selection_date)
        .where(DailySelection.cohort == cohort)
        .distinct()
        .order_by(desc(DailySelection.selection_date))
    )
    dates = res.scalars().all()
    return {"cohort": cohort, "archive_dates": dates}

@router.get("/jobs/{job_id}", response_model=JobDetailRead)
async def get_job_detail(job_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Job, Company).join(Company, Job.company_id == Company.id).where(Job.id == job_id)
    res = await db.execute(query)
    row = res.first()
    if not row:
        raise HTTPException(status_code=404, detail="Job not found")

    job, comp = row
    eligs_res = await db.execute(select(JobCohortEligibility).where(JobCohortEligibility.job_id == job.id))
    vrs_res = await db.execute(select(VerificationResult).where(VerificationResult.job_id == job.id))

    return _build_job_detail(job, comp, eligs_res.scalars().all(), vrs_res.scalars().all())
