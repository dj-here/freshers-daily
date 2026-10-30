from datetime import datetime
from pydantic import BaseModel, EmailStr

class SubscribeRequest(BaseModel):
    email: EmailStr
    cohort: str # "2026", "2027", "2028", "all"

class SubscribeResponse(BaseModel):
    success: bool
    message: str
    email: str
    cohort: str
