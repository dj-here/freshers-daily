from datetime import datetime
from fastapi import APIRouter, Depends, Response, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models import DailySelection, Job, Company
from app.services.rss import generate_cohort_rss_feed

router = APIRouter()

@router.get("/{cohort}.xml")
async def get_cohort_rss(cohort: str, db: AsyncSession = Depends(get_db)):
    if cohort not in ["2026", "2027", "2028"]:
        raise HTTPException(status_code=400, detail="Invalid cohort")

    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    query = (
        select(DailySelection, Job, Company)
        .join(Job, DailySelection.job_id == Job.id)
        .join(Company, Job.company_id == Company.id)
        .where(DailySelection.cohort == cohort)
        .order_by(DailySelection.selection_date.desc(), DailySelection.rank.asc())
        .limit(10)
    )
    res = await db.execute(query)
    items = []
    for ds, job, comp in res.all():
        items.append({
            "title": job.title,
            "company_name": comp.name,
            "normalized_city": job.normalized_city,
            "role_category": job.role_category,
            "stipend_ctc": job.stipend_ctc,
            "trust_score": job.trust_score,
            "apply_url": job.apply_url,
            "final_apply_url": job.final_apply_url
        })

    feed_xml = generate_cohort_rss_feed(cohort, date_str, items)
    return Response(content=feed_xml, media_type="application/xml")
