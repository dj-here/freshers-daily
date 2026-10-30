import hashlib
import json
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.core.config import settings

logger = logging.getLogger(__name__)

# In-memory per-domain rate limiter
_DOMAIN_LAST_REQUEST_TIME: Dict[str, float] = {}

def apply_rate_limit(domain: str, min_delay: float = 1.0):
    now = time.time()
    last = _DOMAIN_LAST_REQUEST_TIME.get(domain, 0.0)
    elapsed = now - last
    if elapsed < min_delay:
        sleep_time = min_delay - elapsed
        time.sleep(sleep_time)
    _DOMAIN_LAST_REQUEST_TIME[domain] = time.time()

@dataclass
class RawJobData:
    external_id: str
    title: str
    location_raw: str
    apply_url: str
    payload_json: str
    raw_html: Optional[str] = None
    content_hash: str = ""
    posted_date: Optional[datetime] = None

    def __post_init__(self):
        if not self.content_hash:
            data = f"{self.title}:{self.location_raw}:{self.payload_json}"
            self.content_hash = hashlib.sha256(data.encode("utf-8")).hexdigest()

class BaseConnector(ABC):
    name: str = "base"

    def __init__(self):
        self.headers = {
            "User-Agent": settings.USER_AGENT,
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
        }
        self.timeout = settings.HTTP_TIMEOUT_SECONDS

    def get_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            headers=self.headers,
            timeout=self.timeout,
            follow_redirects=True,
            max_redirects=settings.MAX_REDIRECTS,
        )

    @abstractmethod
    async def fetch_jobs(self, company_name: str, config: Dict[str, Any]) -> List[RawJobData]:
        """Fetch raw job postings from the ATS endpoint for the given company."""
        pass
