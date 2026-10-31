import asyncio
import json
import httpx

SLUGS = [
    "cred", "groww", "slice", "meesho", "clevertap", "zeta", "dream11",
    "games24x7", "sharechat", "glance", "lenskart", "nykaa", "delhivery",
    "shadowfax", "shiprocket", "spinny", "atherenergy", "olaelectric",
    "rapido", "mpl", "postman", "browserstack", "browserstacksoftware",
    "juspay", "urbancompany", "urbanclap", "zepto", "swiggy", "zomato",
    "paytm", "phonepe", "razorpaysoftwareprivatelimited", "singlestore",
    "hackerrank", "rubrik", "cohesity", "nutanix", "confluent", "cloudera",
    "snowflake", "elastic", "mongodb", "datadog", "pagerduty", "hashicorp"
]

async def check():
    found = []
    async with httpx.AsyncClient(timeout=5.0) as client:
        for s in SLUGS:
            # Try greenhouse
            gh_url = f"https://boards-api.greenhouse.io/v1/boards/{s}/jobs"
            try:
                r = await client.get(gh_url)
                if r.status_code == 200:
                    jobs = r.json().get("jobs", [])
                    print(f"GH [{s}]: {len(jobs)} jobs")
                    found.append(("greenhouse", s, len(jobs)))
            except Exception:
                pass

            # Try lever
            lever_url = f"https://api.lever.co/v0/postings/{s}?mode=json"
            try:
                r = await client.get(lever_url)
                if r.status_code == 200:
                    jobs = r.json()
                    if isinstance(jobs, list):
                        print(f"LEVER [{s}]: {len(jobs)} jobs")
                        found.append(("lever", s, len(jobs)))
            except Exception:
                pass

if __name__ == "__main__":
    asyncio.run(check())
