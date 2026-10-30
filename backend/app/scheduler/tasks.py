import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.pipeline.daily_runner import DailyPipelineRunner
from app.services.email_digest import EmailDigestService
from app.services.telegram import TelegramService

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler(timezone=settings.TIMEZONE)

async def scheduled_ingestion():
    logger.info("Executing scheduled ingestion at 02:00 IST")
    async with AsyncSessionLocal() as session:
        runner = DailyPipelineRunner(session)
        await runner._ingest_sources()

async def scheduled_verification():
    logger.info("Executing scheduled verification at 03:00 IST")
    async with AsyncSessionLocal() as session:
        runner = DailyPipelineRunner(session)
        await runner._verify_pending_jobs()

async def scheduled_daily_publish():
    logger.info("Executing scheduled daily publish at 06:00 IST")
    async with AsyncSessionLocal() as session:
        runner = DailyPipelineRunner(session)
        summary = await runner.run_pipeline(dry_run=False)

        # Trigger delivery channels
        email_svc = EmailDigestService(session)
        await email_svc.send_daily_digests(summary["date"])

        if settings.FEATURE_FLAG_TELEGRAM:
            tg_svc = TelegramService()
            await tg_svc.broadcast_daily_summary(summary)

def start_scheduler():
    if not settings.SCHEDULER_ENABLED:
        logger.info("Scheduler is disabled by config.")
        return

    # Ingestion 02:00 IST
    scheduler.add_job(scheduled_ingestion, CronTrigger(hour=2, minute=0, timezone=settings.TIMEZONE))
    # Verification 03:00 IST
    scheduler.add_job(scheduled_verification, CronTrigger(hour=3, minute=0, timezone=settings.TIMEZONE))
    # Publish 06:00 IST
    scheduler.add_job(scheduled_daily_publish, CronTrigger(hour=6, minute=0, timezone=settings.TIMEZONE))

    scheduler.start()
    logger.info("APScheduler started with daily 02:00, 03:00, 06:00 IST triggers.")
