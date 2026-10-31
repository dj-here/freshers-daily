import asyncio
import httpx
import json

COMPANIES = [
    "stripe", "coinbase", "databricks", "cloudflare", "twilio", "datadog", "gitlab", 
    "mongodb", "elastic", "okta", "razorpaysoftwareprivatelimited", "inmobi", "vercel", 
    "samsara", "asana", "cockroachlabs", "singlestore", "yugabyte", "newrelic", "affirm", 
    "brex", "ramp", "webflow", "klaviyo", "gusto", "checkr", "sumologic", "launchdarkly", 
    "pagerduty", "hackerrank", "rubrik", "cohesity", "nutanix", "confluent", "cloudera", 
    "snowflake", "hashicorp", "uber", "postman", "thoughtworks", "redhat", "adobe",
    "cisco", "atlassian", "salesforce", "servicenow", "workday", "vmware", "intuit",
    "sap", "autodesk", "synopsys", "cadence", "qualcomm", "intel", "amd", "nvidia"
]

async def scan():
    async with httpx.AsyncClient(timeout=6.0) as client:
        for c in COMPANIES:
            try:
                r = await client.get(f"https://boards-api.greenhouse.io/v1/boards/{c}/jobs")
                if r.status_code == 200:
                    jobs = r.json().get("jobs", [])
                    for j in jobs:
                        loc = (j.get("location") or {}).get("name", "").lower()
                        title = j.get("title", "").lower()
                        if any(k in loc for k in ["india", "bengaluru", "bangalore", "hyderabad", "pune", "mumbai", "gurgaon", "delhi", "remote"]):
                            if any(w in title for w in ["intern", "graduate", "trainee", "associate", "junior", "early", "entry", "fresh", "campus", "university"]):
                                print(f"[{c}] {j['title']} ({j.get('location', {}).get('name')}) -> https://job-boards.greenhouse.io/{c}/jobs/{j['id']}")
            except Exception:
                pass

if __name__ == "__main__":
    asyncio.run(scan())
