from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models import Company, Source, Job, RawJob, VerificationResult, JobCohortEligibility, AuditLog
from app.schemas.job import JobDetailRead
from app.schemas.admin import ManualJobSubmitRequest, JobActionRequest, ConnectorHealthStatus
from app.pipeline.verifier import JobVerifier
from app.api.cohorts import _build_job_detail

router = APIRouter()

async def verify_admin_key(x_admin_key: Optional[str] = Header(None)):
    if not x_admin_key or x_admin_key != settings.ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid Admin API Key")
    return x_admin_key

@router.get("/review-queue", response_model=List[JobDetailRead])
async def get_review_queue(
    db: AsyncSession = Depends(get_db),
    admin: str = Depends(verify_admin_key)
):
    query = (
        select(Job, Company)
        .join(Company, Job.company_id == Company.id)
        .where(Job.status == "needs_review")
        .order_by(Job.created_at.desc())
    )
    res = await db.execute(query)
    results = []
    for job, comp in res.all():
        eligs = (await db.execute(select(JobCohortEligibility).where(JobCohortEligibility.job_id == job.id))).scalars().all()
        vrs = (await db.execute(select(VerificationResult).where(VerificationResult.job_id == job.id))).scalars().all()
        results.append(_build_job_detail(job, comp, eligs, vrs))

    return results

@router.post("/jobs/{job_id}/action")
async def take_job_action(
    job_id: int,
    req: JobActionRequest,
    db: AsyncSession = Depends(get_db),
    admin: str = Depends(verify_admin_key)
):
    job = await db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if req.action == "approve":
        job.status = "verified"
        job.trust_score = max(80.0, job.trust_score)
        if req.override_cohort:
            # Update cohort eligibility
            elig = (await db.execute(select(JobCohortEligibility).where(JobCohortEligibility.job_id == job.id))).scalar_one_or_none()
            if elig:
                elig.cohort = req.override_cohort
            else:
                db.add(JobCohortEligibility(
                    job_id=job.id,
                    cohort=req.override_cohort,
                    role_type="full_time",
                    evidence_snippet="Manually approved by Admin",
                    evidence_url=job.final_apply_url or job.apply_url,
                    branches="[\"CSE\", \"IT\"]"
                ))
    elif req.action == "reject":
        job.status = "rejected"
        job.rejection_reason = req.reason or "Rejected by Admin"
    else:
        raise HTTPException(status_code=400, detail="Action must be 'approve' or 'reject'")

    audit = AuditLog(
        admin_user="admin",
        action=f"{req.action}_job",
        target_type="job",
        target_id=str(job_id),
        details=f"Reason: {req.reason or 'None'}"
    )
    db.add(audit)
    await db.commit()

    return {"success": True, "job_id": job_id, "new_status": job.status}

@router.post("/jobs/submit", response_model=JobDetailRead)
async def submit_manual_job(
    req: ManualJobSubmitRequest,
    db: AsyncSession = Depends(get_db),
    admin: str = Depends(verify_admin_key)
):
    verifier = JobVerifier()
    report = await verifier.verify_job(
        title="Software Engineer",
        apply_url=req.url,
        location_raw="India",
        raw_html="",
        company_domain=req.url,
        skip_network_liveness=False
    )

    # Find or create company
    company_name = req.company_name or "Direct Employer"
    comp_res = await db.execute(select(Company).where(Company.name == company_name))
    comp = comp_res.scalar_one_or_none()
    if not comp:
        comp = Company(
            name=company_name,
            slug=company_name.lower().replace(" ", "-"),
            domain=req.url.split("/")[2] if "//" in req.url else "unknown.com",
            tier="TIER_2"
        )
        db.add(comp)
        await db.flush()

    # Create dummy raw job
    raw_job = RawJob(
        source_id=1,
        external_id=f"manual_{datetime.utcnow().timestamp()}",
        title=report.extracted_data.role_type.title() if report.extracted_data else "Software Engineer",
        location_raw="India",
        apply_url=req.url,
        payload_json="{\"manual\": true}",
        content_hash=f"hash_{datetime.utcnow().timestamp()}"
    )
    db.add(raw_job)
    await db.flush()

    job = Job(
        raw_job_id=raw_job.id,
        company_id=comp.id,
        title="Software Engineer",
        role_category=report.role_category,
        normalized_city=report.normalized_loc.city if report.normalized_loc else "India",
        country="India",
        apply_url=req.url,
        final_apply_url=report.final_apply_url or req.url,
        trust_score=report.final_trust_score,
        status=report.status
    )
    db.add(job)
    await db.flush()

    # Save results
    for r in report.results:
        db.add(VerificationResult(
            job_id=job.id,
            check_name=r["check_name"],
            passed=r["passed"],
            score=r["score"],
            reason=r["reason"],
            evidence_quote=r.get("evidence_quote")
        ))

    cohort = req.expected_cohort or (report.extracted_data.eligible_batches[0] if report.extracted_data and report.extracted_data.eligible_batches else "2027")
    db.add(JobCohortEligibility(
        job_id=job.id,
        cohort=cohort,
        role_type=report.extracted_data.role_type if report.extracted_data else "full_time",
        evidence_snippet=report.extracted_data.batch_evidence if report.extracted_data else "Manual submission verification",
        evidence_url=job.final_apply_url or job.apply_url,
        branches="[\"CSE\", \"IT\"]"
    ))

    await db.commit()

    eligs = (await db.execute(select(JobCohortEligibility).where(JobCohortEligibility.job_id == job.id))).scalars().all()
    vrs = (await db.execute(select(VerificationResult).where(VerificationResult.job_id == job.id))).scalars().all()
    return _build_job_detail(job, comp, eligs, vrs)

@router.get("/sources/health", response_model=List[ConnectorHealthStatus])
async def get_sources_health(
    db: AsyncSession = Depends(get_db),
    admin: str = Depends(verify_admin_key)
):
    query = select(Source, Company).join(Company, Source.company_id == Company.id).limit(100)
    res = await db.execute(query)
    health_list = []
    for src, comp in res.all():
        health_list.append(ConnectorHealthStatus(
            source_id=src.id,
            company_name=comp.name,
            source_type=src.source_type,
            status=src.status,
            last_polled_at=src.last_polled_at,
            recent_jobs_count=0
        ))
    return health_list

@router.patch("/companies/{company_id}/tier")
async def update_company_tier(
    company_id: int,
    tier: str,
    db: AsyncSession = Depends(get_db),
    admin: str = Depends(verify_admin_key)
):
    if tier not in ["TIER_1", "TIER_2", "TIER_3", "TIER_OTHER"]:
        raise HTTPException(status_code=400, detail="Invalid tier")

    comp = await db.get(Company, company_id)
    if not comp:
        raise HTTPException(status_code=404, detail="Company not found")

    comp.tier = tier
    await db.commit()
    return {"success": True, "company_id": company_id, "tier": tier}
