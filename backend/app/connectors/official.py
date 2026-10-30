import json
import logging
from datetime import datetime
from typing import Any, Dict, List
from urllib.parse import urlparse
import httpx
from bs4 import BeautifulSoup
from app.connectors.base import BaseConnector, RawJobData, apply_rate_limit

logger = logging.getLogger(__name__)

class OfficialCareerConnector(BaseConnector):
    name = "official"

    async def fetch_jobs(self, company_name: str, config: Dict[str, Any]) -> List[RawJobData]:
        base_url = config.get("base_url")
        if not base_url:
            return []

        domain = urlparse(base_url).netloc
        apply_rate_limit(domain)

        raw_jobs = []
        async with self.get_client() as client:
            try:
                response = await client.get(base_url)
                if response.status_code != 200:
                    return []

                content_type = response.headers.get("content-type", "")
                if "application/json" in content_type:
                    data = response.json()
                    # Generic JSON extraction if list
                    items = data if isinstance(data, list) else data.get("jobs", data.get("items", []))
                    for idx, item in enumerate(items[:20]):
                        if isinstance(item, dict):
                            title = item.get("title", item.get("role", "Software Engineer"))
                            apply_url = item.get("url", item.get("apply_url", base_url))
                            raw_jobs.append(
                                RawJobData(
                                    external_id=str(item.get("id", idx)),
                                    title=title,
                                    location_raw=str(item.get("location", "India")),
                                    apply_url=apply_url,
                                    payload_json=json.dumps(item),
                                    raw_html="",
                                    posted_date=datetime.utcnow()
                                )
                            )
                else:
                    # HTML extraction
                    soup = BeautifulSoup(response.text, "html.parser")
                    # Collect anchor links that look like software jobs
                    links = soup.find_all("a", href=True)
                    for idx, a in enumerate(links):
                        text = a.get_text(strip=True)
                        href = a["href"]
                        if any(k in text.lower() for k in ["engineer", "developer", "trainee", "intern", "sde"]):
                            if not href.startswith("http"):
                                href = f"https://{domain.rstrip('/')}/{href.lstrip('/')}"
                            raw_jobs.append(
                                RawJobData(
                                    external_id=f"html_{idx}",
                                    title=text,
                                    location_raw="India",
                                    apply_url=href,
                                    payload_json=json.dumps({"title": text, "url": href}),
                                    raw_html=response.text[:2000],
                                    posted_date=datetime.utcnow()
                                )
                            )
                            if len(raw_jobs) >= 10:
                                break
            except Exception as e:
                logger.error(f"Error fetching official portal for {company_name}: {e}")

        return raw_jobs
