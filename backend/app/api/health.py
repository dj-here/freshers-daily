from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models import Company, Source, Job

router = APIRouter()

_START_TIME = datetime.utcnow()

@router.get("")
async def get_health(db: AsyncSession = Depends(get_db)):
    comp_count = (await db.execute(select(func.count(Company.id)))).scalar_one()
    src_count = (await db.execute(select(func.count(Source.id)))).scalar_one()
    job_count = (await db.execute(select(func.count(Job.id)))).scalar_one()
    verified_count = (await db.execute(select(func.count(Job.id)).where(Job.status == "verified"))).scalar_one()
    published_count = (await db.execute(select(func.count(Job.id)).where(Job.status == "published"))).scalar_one()
    review_count = (await db.execute(select(func.count(Job.id)).where(Job.status == "needs_review"))).scalar_one()
    rejected_count = (await db.execute(select(func.count(Job.id)).where(Job.status == "rejected"))).scalar_one()

    uptime_seconds = int((datetime.utcnow() - _START_TIME).total_seconds())

    return {
        "status": "healthy",
        "app": "FreshersDaily",
        "uptime_seconds": uptime_seconds,
        "database": {
            "companies": comp_count,
            "sources": src_count,
            "jobs_total": job_count,
            "published": published_count,
            "verified": verified_count,
            "needs_review": review_count,
            "rejected": rejected_count
        }
    }
