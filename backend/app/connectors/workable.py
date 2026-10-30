import json
import logging
from datetime import datetime
from typing import Any, Dict, List
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.connectors.base import BaseConnector, RawJobData, apply_rate_limit

logger = logging.getLogger(__name__)

class WorkableConnector(BaseConnector):
    name = "workable"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)),
        reraise=False
    )
    async def fetch_jobs(self, company_name: str, config: Dict[str, Any]) -> List[RawJobData]:
        shortcode = config.get("shortcode") or config.get("slug")
        if not shortcode:
            logger.warning(f"WorkableConnector: missing shortcode for {company_name}")
            return []

        url = f"https://apply.workable.com/api/v1/widget/accounts/{shortcode}"
        domain = "apply.workable.com"
        apply_rate_limit(domain)

        raw_jobs = []
        async with self.get_client() as client:
            try:
                response = await client.get(url)
                if response.status_code == 404:
                    return []
                response.raise_for_status()
                data = response.json()
                jobs = data.get("jobs", [])

                for item in jobs:
                    external_id = str(item.get("shortcode") or item.get("id"))
                    title = item.get("title", "")
                    city = item.get("city", "")
                    country = item.get("country", "")
                    telecommuting = item.get("telecommuting", False)
                    location_raw = f"{city}, {country}".strip(", ")
                    if telecommuting:
                        location_raw = f"{location_raw} (Remote)".strip()
                        
                    apply_url = item.get("url") or f"https://apply.workable.com/{shortcode}/j/{external_id}/"
                    
                    posted_date = None
                    if item.get("published_on"):
                        try:
                            posted_date = datetime.fromisoformat(item["published_on"].replace("Z", "+00:00"))
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
                logger.error(f"Error fetching workable jobs for {company_name} ({shortcode}): {e}")

        return raw_jobs
