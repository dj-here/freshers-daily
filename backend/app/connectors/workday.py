import json
import logging
from datetime import datetime
from typing import Any, Dict, List
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.connectors.base import BaseConnector, RawJobData, apply_rate_limit

logger = logging.getLogger(__name__)

class WorkdayConnector(BaseConnector):
    name = "workday"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)),
        reraise=False
    )
    async def fetch_jobs(self, company_name: str, config: Dict[str, Any]) -> List[RawJobData]:
        tenant = config.get("tenant") or config.get("slug")
        site = config.get("site", "External")
        host = config.get("host", f"{tenant}.myworkdayjobs.com")
        if not tenant:
            logger.warning(f"WorkdayConnector: missing tenant for {company_name}")
            return []

        # Public CXS endpoint
        url = f"https://{host}/wday/cxs/{tenant}/{site}/jobs"
        domain = host
        apply_rate_limit(domain)

        payload = {
            "appliedFacets": {},
            "limit": 50,
            "offset": 0,
            "searchText": "India"
        }

        raw_jobs = []
        async with self.get_client() as client:
            try:
                response = await client.post(url, json=payload)
                if response.status_code == 404:
                    return []
                response.raise_for_status()
                data = response.json()
                job_postings = data.get("jobPostings", [])

                for item in job_postings:
                    external_path = item.get("externalPath", "")
                    title = item.get("title", "")
                    location_raw = item.get("locationsText", "")
                    bullet_fields = item.get("bulletFields", [])
                    if not location_raw and bullet_fields:
                        location_raw = ", ".join(bullet_fields)

                    apply_url = f"https://{host}/en-US/{tenant}/{site}{external_path}"
                    
                    posted_date = None
                    posted_on = item.get("postedOn")
                    if posted_on:
                        # Workday often gives 'Posted Today', 'Posted 3 Days Ago'
                        pass

                    raw_jobs.append(
                        RawJobData(
                            external_id=external_path.strip("/"),
                            title=title,
                            location_raw=location_raw,
                            apply_url=apply_url,
                            payload_json=json.dumps(item),
                            raw_html="",
                            posted_date=datetime.utcnow()
                        )
                    )
            except Exception as e:
                logger.error(f"Error fetching workday jobs for {company_name} ({tenant}): {e}")

        return raw_jobs
