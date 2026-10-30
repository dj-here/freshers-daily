import json
import logging
from datetime import datetime
from typing import Any, Dict, List
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.connectors.base import BaseConnector, RawJobData, apply_rate_limit

logger = logging.getLogger(__name__)

class GreenhouseConnector(BaseConnector):
    name = "greenhouse"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)),
        reraise=False
    )
    async def fetch_jobs(self, company_name: str, config: Dict[str, Any]) -> List[RawJobData]:
        board_token = config.get("board_token") or config.get("slug")
        if not board_token:
            logger.warning(f"GreenhouseConnector: missing board_token for {company_name}")
            return []

        url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=true"
        domain = "boards-api.greenhouse.io"
        apply_rate_limit(domain)

        raw_jobs = []
        async with self.get_client() as client:
            try:
                response = await client.get(url)
                if response.status_code == 404:
                    logger.warning(f"Greenhouse board not found for {board_token}")
                    return []
                response.raise_for_status()
                data = response.json()
                jobs = data.get("jobs", [])

                for item in jobs:
                    external_id = str(item.get("id"))
                    title = item.get("title", "")
                    loc = item.get("location", {})
                    location_raw = loc.get("name", "") if isinstance(loc, dict) else str(loc)
                    apply_url = item.get("absolute_url") or f"https://boards.greenhouse.io/{board_token}/jobs/{external_id}"
                    
                    # Optional updated_at date
                    posted_date = None
                    if item.get("updated_at"):
                        try:
                            posted_date = datetime.fromisoformat(item["updated_at"].replace("Z", "+00:00"))
                        except Exception:
                            pass

                    raw_jobs.append(
                        RawJobData(
                            external_id=external_id,
                            title=title,
                            location_raw=location_raw,
                            apply_url=apply_url,
                            payload_json=json.dumps(item),
                            raw_html=item.get("content", ""),
                            posted_date=posted_date
                        )
                    )
            except Exception as e:
                logger.error(f"Error fetching greenhouse jobs for {company_name} ({board_token}): {e}")

        return raw_jobs
