from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class RawJob(Base):
    __tablename__ = "raw_jobs"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id", ondelete="CASCADE"), nullable=False)
    external_id = Column(String(255), nullable=False, index=True)
    title = Column(String(512), nullable=False)
    location_raw = Column(String(512), nullable=True)
    apply_url = Column(String(2048), nullable=False)
    payload_json = Column(Text, nullable=False) # Serialized raw JSON payload from ATS
    raw_html = Column(Text, nullable=True)     # Raw HTML if fetched via scraper
    content_hash = Column(String(64), nullable=False, index=True) # SHA256 of text/payload
    first_seen_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    source = relationship("Source", back_populates="raw_jobs")
    jobs = relationship("Job", back_populates="raw_job", cascade="all, delete-orphan")
