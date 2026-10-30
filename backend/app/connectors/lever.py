import json
import logging
from datetime import datetime
from typing import Any, Dict, List
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.connectors.base import BaseConnector, RawJobData, apply_rate_limit

logger = logging.getLogger(__name__)

class LeverConnector(BaseConnector):
    name = "lever"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)),
        reraise=False
    )
    async def fetch_jobs(self, company_name: str, config: Dict[str, Any]) -> List[RawJobData]:
        site = config.get("site") or config.get("slug")
        if not site:
            logger.warning(f"LeverConnector: missing site for {company_name}")
            return []

        url = f"https://api.lever.co/v0/postings/{site}?mode=json"
        domain = "api.lever.co"
        apply_rate_limit(domain)

        raw_jobs = []
        async with self.get_client() as client:
            try:
                response = await client.get(url)
                if response.status_code == 404:
                    logger.warning(f"Lever site not found: {site}")
                    return []
                response.raise_for_status()
                postings = response.json()
                if not isinstance(postings, list):
                    return []

                for item in postings:
                    external_id = str(item.get("id"))
                    title = item.get("text", "")
                    cats = item.get("categories", {})
                    location_raw = cats.get("location", "") if isinstance(cats, dict) else ""
                    apply_url = item.get("hostedUrl") or item.get("applyUrl") or f"https://jobs.lever.co/{site}/{external_id}"
                    
                    posted_date = None
                    if item.get("createdAt"):
                        try:
                            # Lever createdAt is epoch ms
                            posted_date = datetime.fromtimestamp(item["createdAt"] / 1000.0)
                        except Exception:
                            pass

                    description = item.get("descriptionPlain") or item.get("description", "")

                    raw_jobs.append(
                        RawJobData(
                            external_id=external_id,
                            title=title,
                            location_raw=location_raw,
                            apply_url=apply_url,
                            payload_json=json.dumps(item),
                            raw_html=description,
                            posted_date=posted_date
                        )
                    )
            except Exception as e:
                logger.error(f"Error fetching lever jobs for {company_name} ({site}): {e}")

        return raw_jobs
