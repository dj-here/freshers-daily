import hashlib
import json
import logging
from datetime import datetime
from typing import Any, Dict, List
import httpx
from bs4 import BeautifulSoup
from app.connectors.base import BaseConnector, RawJobData

logger = logging.getLogger(__name__)

class ManualSubmitConnector(BaseConnector):
    name = "manual"

    async def fetch_jobs(self, company_name: str, config: Dict[str, Any]) -> List[RawJobData]:
        url = config.get("url")
        if not url:
            return []

        async with self.get_client() as client:
            try:
                response = await client.get(url)
                soup = BeautifulSoup(response.text, "html.parser")
                title = soup.title.string.strip() if soup.title and soup.title.string else "Software Engineer"
                
                # Check for h1 tags
                h1 = soup.find("h1")
                if h1 and h1.get_text(strip=True):
                    title = h1.get_text(strip=True)

                body_text = soup.get_text(separator=" ", strip=True)
                ext_id = hashlib.md5(url.encode("utf-8")).hexdigest()[:16]

                return [
                    RawJobData(
                        external_id=ext_id,
                        title=title,
                        location_raw="India",
                        apply_url=url,
                        payload_json=json.dumps({"url": url, "title": title, "manual": True}),
                        raw_html=body_text[:10000],
                        posted_date=datetime.utcnow()
                    )
                ]
            except Exception as e:
                logger.error(f"Error fetching manual job url {url}: {e}")
                return []
