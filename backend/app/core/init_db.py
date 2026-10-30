import logging
from app.core.database import engine, Base
from app.models import *

logger = logging.getLogger(__name__)

async def init_db() -> None:
    """Create all tables if they don't already exist."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables initialized successfully.")
