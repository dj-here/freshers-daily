from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    domain = Column(String(255), nullable=False, index=True)
    tier = Column(String(50), default="TIER_OTHER", nullable=False) # TIER_1, TIER_2, TIER_3, TIER_OTHER
    logo_url = Column(String(1024), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    sources = relationship("Source", back_populates="company", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="company", cascade="all, delete-orphan")
