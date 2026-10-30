from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

class VerificationResultRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    check_name: str
    passed: bool
    score: float
    reason: str
    evidence_quote: Optional[str] = None
    checked_at: datetime


class JobCohortEligibilityRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cohort: str
    role_type: str
    evidence_snippet: str
    evidence_url: str
    min_exp_years: float
    max_exp_years: float
    branches: str
    degree_requirements: Optional[str] = None


class JobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_name: str
    company_slug: str
    company_tier: str
    company_domain: str
    title: str
    role_category: str
    normalized_city: str
    state: Optional[str] = None
    country: str = "India"
    is_remote: bool
    is_hybrid: bool
    apply_url: str
    final_apply_url: Optional[str] = None
    stipend_ctc: Optional[str] = None
    stipend_ctc_evidence: Optional[str] = None
    deadline: Optional[datetime] = None
    deadline_evidence: Optional[str] = None
    trust_score: float
    status: str
    created_at: datetime


class JobDetailRead(JobRead):
    cohort_eligibilities: List[JobCohortEligibilityRead] = []
    verification_results: List[VerificationResultRead] = []
