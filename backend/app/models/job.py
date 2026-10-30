from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base, SafeVectorType

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    raw_job_id = Column(Integer, ForeignKey("raw_jobs.id", ondelete="CASCADE"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(512), nullable=False, index=True)
    role_category = Column(String(100), nullable=False, index=True) # SDE, Backend, Frontend, Fullstack, Mobile, QA/SDET, DevOps/Cloud, Data Engineer, ML/AI, Security, GET/ASE
    normalized_city = Column(String(100), nullable=False, index=True)
    state = Column(String(100), nullable=True)
    country = Column(String(50), default="India", nullable=False)
    is_remote = Column(Boolean, default=False, nullable=False)
    is_hybrid = Column(Boolean, default=False, nullable=False)
    apply_url = Column(String(2048), nullable=False)
    final_apply_url = Column(String(2048), nullable=True)
    stipend_ctc = Column(String(255), nullable=True)
    stipend_ctc_evidence = Column(Text, nullable=True)
    deadline = Column(DateTime, nullable=True)
    deadline_evidence = Column(Text, nullable=True)
    trust_score = Column(Float, default=0.0, nullable=False)
    embedding = Column(SafeVectorType(1536), nullable=True)
    status = Column(String(50), default="pending", nullable=False, index=True) # pending, verified, published, rejected, needs_review
    rejection_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    company = relationship("Company", back_populates="jobs")
    raw_job = relationship("RawJob", back_populates="jobs")
    cohort_eligibilities = relationship("JobCohortEligibility", back_populates="job", cascade="all, delete-orphan")
    verification_results = relationship("VerificationResult", back_populates="job", cascade="all, delete-orphan")
    daily_selections = relationship("DailySelection", back_populates="job", cascade="all, delete-orphan")
    link_checks = relationship("LinkCheckLog", back_populates="job", cascade="all, delete-orphan")


class JobCohortEligibility(Base):
    __tablename__ = "job_cohort_eligibility"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    cohort = Column(String(10), nullable=False, index=True) # "2026", "2027", "2028"
    role_type = Column(String(50), nullable=False) # "full_time", "internship", "internship_ppo"
    evidence_snippet = Column(Text, nullable=False) # STRICT verbatim quote from source
    evidence_url = Column(String(2048), nullable=False)
    min_exp_years = Column(Float, default=0.0, nullable=False)
    max_exp_years = Column(Float, default=1.0, nullable=False)
    branches = Column(Text, default="[]", nullable=False) # JSON string e.g. ["CSE", "IT"]
    degree_requirements = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    job = relationship("Job", back_populates="cohort_eligibilities")


class VerificationResult(Base):
    __tablename__ = "verification_results"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    check_name = Column(String(100), nullable=False) # liveness, domain_trust, scam_filter, fresher_eligibility, location_normalizer, freshness, role_relevance
    passed = Column(Boolean, nullable=False)
    score = Column(Float, default=0.0, nullable=False)
    reason = Column(Text, nullable=False)
    evidence_quote = Column(Text, nullable=True)
    checked_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    job = relationship("Job", back_populates="verification_results")


class DailySelection(Base):
    __tablename__ = "daily_selections"

    id = Column(Integer, primary_key=True, index=True)
    selection_date = Column(String(10), nullable=False, index=True) # "YYYY-MM-DD"
    cohort = Column(String(10), nullable=False, index=True) # "2026", "2027", "2028"
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    rank = Column(Integer, nullable=False) # 1 to 5
    final_score = Column(Float, nullable=False)
    selection_explanation = Column(Text, nullable=False) # Explanatory text/JSON for why it was selected
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    job = relationship("Job", back_populates="daily_selections")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, index=True)
    cohort = Column(String(10), nullable=False, index=True) # "2026", "2027", "2028", "all"
    is_active = Column(Boolean, default=True, nullable=False)
    token = Column(String(128), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class LinkCheckLog(Base):
    __tablename__ = "link_check_logs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    checked_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    http_status = Column(Integer, nullable=False)
    is_active = Column(Boolean, nullable=False)
    closure_detected = Column(Boolean, default=False, nullable=False)
    final_url = Column(String(2048), nullable=False)
    notes = Column(Text, nullable=True)

    job = relationship("Job", back_populates="link_checks")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    admin_user = Column(String(100), nullable=False)
    action = Column(String(100), nullable=False) # approve_job, reject_job, update_tier, submit_manual_job, trigger_ingestion
    target_type = Column(String(50), nullable=False)
    target_id = Column(String(100), nullable=False)
    details = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
