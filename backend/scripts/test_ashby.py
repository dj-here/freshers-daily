import asyncio
import httpx

ASHBY_COMPANIES = ["sarvam", "hasura", "yellowai", "koreai", "krutrim", "zepto", "groww", "navi"]

async def test_ashby():
    async with httpx.AsyncClient(timeout=5.0) as client:
        for c in ASHBY_COMPANIES:
            try:
                r = await client.get(f"https://api.ashbyhq.com/posting-api/job-board/{c}")
                if r.status_code == 200:
                    jobs = r.json().get("jobs", [])
                    print(f"Ashby [{c}]: {len(jobs)} jobs")
                    for j in jobs:
                        loc = (j.get("locationName") or "").lower()
                        title = (j.get("title") or "").lower()
                        if any(k in loc for k in ["india", "bengaluru", "bangalore"]):
                            print(f"   -> {j.get('title')} ({j.get('locationName')}) | {j.get('jobUrl')}")
            except Exception as e:
                pass

if __name__ == "__main__":
    asyncio.run(test_ashby())
