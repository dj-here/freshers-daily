import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.init_db import init_db
from app.scheduler.tasks import start_scheduler
from app.api.cohorts import router as cohorts_router
from app.api.subscriptions import router as subscriptions_router
from app.api.admin import router as admin_router
from app.api.feeds import router as feeds_router
from app.api.health import router as health_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("freshers_daily")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing FreshersDaily application...")
    await init_db()
    start_scheduler()
    yield
    logger.info("Shutting down FreshersDaily application...")

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="FreshersDaily API — 5 daily verified software jobs in India for 2026, 2027, and 2028 batches.",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routes
app.include_router(cohorts_router, prefix=f"{settings.API_V1_STR}/cohorts", tags=["Cohorts"])
app.include_router(subscriptions_router, prefix=f"{settings.API_V1_STR}/subscriptions", tags=["Subscriptions"])
app.include_router(admin_router, prefix=f"{settings.API_V1_STR}/admin", tags=["Admin"])
app.include_router(feeds_router, prefix="/feed", tags=["RSS Feeds"])
app.include_router(health_router, prefix="/health", tags=["Health"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to FreshersDaily API",
        "cohorts": ["2026", "2027", "2028"],
        "docs": "/docs",
        "health": "/health"
    }
