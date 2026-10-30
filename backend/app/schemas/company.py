from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict

class CompanyBase(BaseModel):
    name: str
    slug: str
    domain: str
    tier: str = "TIER_OTHER"
    logo_url: Optional[str] = None
    is_active: bool = True

class CompanyCreate(CompanyBase):
    pass

class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    tier: Optional[str] = None
    logo_url: Optional[str] = None
    is_active: Optional[bool] = None

class CompanyRead(CompanyBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime

class SourceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int
    source_type: str
    base_url: Optional[str] = None
    config_json: str
    is_active: bool
    last_polled_at: Optional[datetime] = None
    status: str
