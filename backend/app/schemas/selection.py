from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from app.schemas.job import JobDetailRead

class DailySelectionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    selection_date: str
    cohort: str
    rank: int
    final_score: float
    selection_explanation: str
    published_at: Optional[datetime] = None
    job: JobDetailRead

class CohortDailyFeedResponse(BaseModel):
    date: str
    cohort: str
    verified_count: int
    is_complete: bool # True if exactly 5
    message: Optional[str] = None # e.g. "Only 3 verified openings today"
    today_openings: List[DailySelectionRead]
    still_open_fallback: List[DailySelectionRead] = []
