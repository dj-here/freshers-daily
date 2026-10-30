import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_NAME: str = "FreshersDaily"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "dev-secret-key-change-in-production-min-32-chars"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./freshers_daily.db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # LLM Settings
    LLM_PROVIDER: str = "dummy"  # "anthropic", "openai", "dummy"
    ANTHROPIC_API_KEY: Optional[str] = None
    LLM_MODEL: str = "claude-3-5-sonnet-20241022"
    OPENAI_API_KEY: Optional[str] = None
    LLM_TEMPERATURE: float = 0.0
    LLM_MAX_TOKENS: int = 1500
    LLM_BUDGET_LIMIT_USD_PER_DAY: float = 10.0

    # Ingestion & Scraping
    USER_AGENT: str = "FreshersDailyBot/1.0 (+https://freshersdaily.in/bot; contact@freshersdaily.in)"
    RATE_LIMIT_PER_DOMAIN_SECONDS: float = 1.0
    HTTP_TIMEOUT_SECONDS: float = 15.0
    MAX_REDIRECTS: int = 5

    # Aggregator API Keys (behind feature flags)
    FEATURE_FLAG_ADZUNA: bool = False
    ADZUNA_APP_ID: Optional[str] = None
    ADZUNA_APP_KEY: Optional[str] = None

    # Delivery
    EMAIL_PROVIDER: str = "resend"
    RESEND_API_KEY: Optional[str] = None
    FROM_EMAIL: str = "digest@freshersdaily.in"

    FEATURE_FLAG_TELEGRAM: bool = False
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_CHANNEL_ID_2026: Optional[str] = None
    TELEGRAM_CHANNEL_ID_2027: Optional[str] = None
    TELEGRAM_CHANNEL_ID_2028: Optional[str] = None

    # Admin
    ADMIN_API_KEY: str = "adminkey-dev-supersecret-freshersdaily-2026"

    # Scheduler & Timezone
    SCHEDULER_ENABLED: bool = False
    TIMEZONE: str = "Asia/Kolkata"

    # Ranking Weights File
    RANKING_WEIGHTS_PATH: str = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
        "config",
        "ranking_weights.yaml"
    )
    SEED_COMPANIES_PATH: str = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
        "config",
        "seed_companies.json"
    )

settings = Settings()
