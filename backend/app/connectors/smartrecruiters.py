import json
import logging
from datetime import datetime
from typing import Any, Dict, List
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.connectors.base import BaseConnector, RawJobData, apply_rate_limit

logger = logging.getLogger(__name__)

class SmartRecruitersConnector(BaseConnector):
    name = "smartrecruiters"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)),
        reraise=False
    )
    async def fetch_jobs(self, company_name: str, config: Dict[str, Any]) -> List[RawJobData]:
        company_id = config.get("company_id") or config.get("slug")
        if not company_id:
            logger.warning(f"SmartRecruitersConnector: missing company_id for {company_name}")
            return []

        url = f"https://api.smartrecruiters.com/v1/companies/{company_id}/postings"
        domain = "api.smartrecruiters.com"
        apply_rate_limit(domain)

        raw_jobs = []
        async with self.get_client() as client:
            try:
                response = await client.get(url, params={"limit": 100})
                if response.status_code == 404:
                    return []
                response.raise_for_status()
                data = response.json()
                postings = data.get("content", [])

                for item in postings:
                    external_id = str(item.get("id"))
                    title = item.get("name", "")
                    loc_dict = item.get("location", {})
                    city = loc_dict.get("city", "")
                    country = loc_dict.get("country", "")
                    location_raw = f"{city}, {country}".strip(", ")
                    
                    apply_url = f"https://jobs.smartrecruiters.com/{company_id}/{external_id}"
                    
                    posted_date = None
                    if item.get("releasedDate"):
                        try:
                            posted_date = datetime.fromisoformat(item["releasedDate"].replace("Z", "+00:00"))
                        except Exception:
                            pass

                    raw_jobs.append(
                        RawJobData(
                            external_id=external_id,
                            title=title,
                            location_raw=location_raw,
                            apply_url=apply_url,
                            payload_json=json.dumps(item),
                            raw_html="",
                            posted_date=posted_date
                        )
                    )
            except Exception as e:
                logger.error(f"Error fetching smartrecruiters jobs for {company_name} ({company_id}): {e}")

        return raw_jobs
