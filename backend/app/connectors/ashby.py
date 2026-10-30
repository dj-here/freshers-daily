import json
import logging
from datetime import datetime
from typing import Any, Dict, List
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.connectors.base import BaseConnector, RawJobData, apply_rate_limit

logger = logging.getLogger(__name__)

class AshbyConnector(BaseConnector):
    name = "ashby"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)),
        reraise=False
    )
    async def fetch_jobs(self, company_name: str, config: Dict[str, Any]) -> List[RawJobData]:
        board_name = config.get("job_board_name") or config.get("slug")
        if not board_name:
            logger.warning(f"AshbyConnector: missing job_board_name for {company_name}")
            return []

        url = "https://jobs.ashbyhq.com/api/non-user-graphql?op=ApiJobBoardWithTeams"
        domain = "jobs.ashbyhq.com"
        apply_rate_limit(domain)

        graphql_query = {
            "operationName": "ApiJobBoardWithTeams",
            "variables": {
                "organizationHostedJobsPageName": board_name
            },
            "query": """
            query ApiJobBoardWithTeams($organizationHostedJobsPageName: String!) {
              jobBoard: jobBoardWithTeams(organizationHostedJobsPageName: $organizationHostedJobsPageName) {
                jobPostings {
                  id
                  title
                  locationName
                  jobUrl
                  publishedAt
                  isRemote
                  secondaryLocations {
                    locationName
                  }
                }
              }
            }
            """
        }

        raw_jobs = []
        async with self.get_client() as client:
            try:
                response = await client.post(url, json=graphql_query)
                if response.status_code == 404:
                    return []
                response.raise_for_status()
                data = response.json()
                board = data.get("data", {}).get("jobBoard")
                if not board:
                    return []

                postings = board.get("jobPostings", [])
                for item in postings:
                    external_id = str(item.get("id"))
                    title = item.get("title", "")
                    loc = item.get("locationName", "")
                    if item.get("isRemote"):
                        loc = f"{loc} (Remote)".strip()
                    apply_url = item.get("jobUrl") or f"https://jobs.ashbyhq.com/{board_name}/{external_id}"
                    
                    posted_date = None
                    if item.get("publishedAt"):
                        try:
                            posted_date = datetime.fromisoformat(item["publishedAt"].replace("Z", "+00:00"))
                        except Exception:
                            pass

                    raw_jobs.append(
                        RawJobData(
                            external_id=external_id,
                            title=title,
                            location_raw=loc,
                            apply_url=apply_url,
                            payload_json=json.dumps(item),
                            raw_html="",
                            posted_date=posted_date
                        )
                    )
            except Exception as e:
                logger.error(f"Error fetching ashby jobs for {company_name} ({board_name}): {e}")

        return raw_jobs
