import json
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.types import TypeDecorator, Text
from app.core.config import settings

# Database Engine
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    connect_args=connect_args,
    future=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Custom Vector Storage Adapter (Postgres pgvector with SQLite fallback)
class SafeVectorType(TypeDecorator):
    impl = Text
    cache_ok = True

    def __init__(self, dim=1536, *args, **kwargs):
        self.dim = dim
        super().__init__(*args, **kwargs)

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, (list, tuple)):
            return json.dumps(list(value))
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, str):
            try:
                return json.loads(value)
            except Exception:
                return value
        return value
