from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, HttpUrl
from app.schemas.job import JobDetailRead

class ManualJobSubmitRequest(BaseModel):
    url: str
    company_name: Optional[str] = None
    expected_cohort: Optional[str] = None # "2026", "2027", "2028"

class JobActionRequest(BaseModel):
    action: str # "approve", "reject"
    reason: Optional[str] = None
    override_cohort: Optional[str] = None

class ConnectorHealthStatus(BaseModel):
    source_id: int
    company_name: str
    source_type: str
    status: str # healthy, degraded, failing
    last_polled_at: Optional[datetime] = None
    recent_jobs_count: int = 0
