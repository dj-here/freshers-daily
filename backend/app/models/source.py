from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    source_type = Column(String(50), nullable=False) # greenhouse, lever, ashby, smartrecruiters, workable, workday, official, aggregator, manual
    base_url = Column(String(1024), nullable=True)
    config_json = Column(Text, default="{}", nullable=False) # JSON string of connector config (slug, board_token, etc.)
    is_active = Column(Boolean, default=True, nullable=False)
    last_polled_at = Column(DateTime, nullable=True)
    status = Column(String(50), default="healthy", nullable=False) # healthy, degraded, failing
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    company = relationship("Company", back_populates="sources")
    raw_jobs = relationship("RawJob", back_populates="source", cascade="all, delete-orphan")
