import asyncio
import json
import httpx

BOARDS = [
    "stripe", "figma", "coinbase", "databricks", "cloudflare", "twilio", 
    "datadog", "gitlab", "mongodb", "elastic", "okta", "razorpaysoftwareprivatelimited",
    "inmobi", "vercel", "purestorage", "samsara", "asana", "cockroachlabs",
    "singlestore", "yugabyte", "newrelic", "affirm", "brex", "ramp",
    "webflow", "klaviyo", "gusto", "checkr", "sumologic", "launchdarkly", "pagerduty"
]

INDIA_KEYWORDS = ["india", "bengaluru", "bangalore", "hyderabad", "pune", "mumbai", "gurgaon", "gurugram", "noida", "delhi"]

async def find_all_india():
    india_jobs = []
    async with httpx.AsyncClient(timeout=12.0) as client:
        for b in BOARDS:
            try:
                url = f"https://boards-api.greenhouse.io/v1/boards/{b}/jobs"
                r = await client.get(url)
                if r.status_code == 200:
                    jobs = r.json().get("jobs", [])
                    for j in jobs:
                        loc = (j.get("location") or {}).get("name", "").lower()
                        if any(k in loc for k in INDIA_KEYWORDS):
                            india_jobs.append({
                                "board": b,
                                "id": j.get("id"),
                                "title": j.get("title"),
                                "location": j.get("location", {}).get("name"),
                                "url": j.get("absolute_url")
                            })
            except Exception as e:
                pass
                
    print(f"Total India jobs found: {len(india_jobs)}")
    with open("greenhouse_india_all.json", "w", encoding="utf-8") as f:
        json.dump(india_jobs, f, indent=2)
    for j in india_jobs:
        print(f"[{j['board']}] {j['title']} ({j['location']}) -> {j['url']}")

if __name__ == "__main__":
    asyncio.run(find_all_india())
