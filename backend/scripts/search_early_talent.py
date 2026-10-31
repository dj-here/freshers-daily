import asyncio
import json
import httpx

BOARDS = [
    ("inmobi", "https://boards-api.greenhouse.io/v1/boards/inmobi/jobs?content=true"),
    ("browserstack", "https://boards-api.greenhouse.io/v1/boards/browserstack/jobs?content=true"),
    ("postman", "https://boards-api.greenhouse.io/v1/boards/postman/jobs?content=true"),
    ("atlassian", "https://boards-api.greenhouse.io/v1/boards/atlassian/jobs?content=true"),
    ("databricks", "https://boards-api.greenhouse.io/v1/boards/databricks/jobs?content=true"),
    ("mongodb", "https://boards-api.greenhouse.io/v1/boards/mongodb/jobs?content=true"),
    ("sprinklr", "https://boards-api.greenhouse.io/v1/boards/sprinklr/jobs?content=true"),
    ("cloudflare", "https://boards-api.greenhouse.io/v1/boards/cloudflare/jobs?content=true"),
    ("snowflake", "https://boards-api.greenhouse.io/v1/boards/snowflake/jobs?content=true"),
    ("elastic", "https://boards-api.greenhouse.io/v1/boards/elastic/jobs?content=true"),
    ("twilio", "https://boards-api.greenhouse.io/v1/boards/twilio/jobs?content=true"),
    ("urbancompany", "https://boards-api.greenhouse.io/v1/boards/urbancompany/jobs?content=true"),
    ("juspay", "https://boards-api.greenhouse.io/v1/boards/juspay/jobs?content=true"),
    ("clevertap", "https://api.lever.co/v0/postings/clevertap?mode=json"),
    ("cred", "https://api.lever.co/v0/postings/cred?mode=json"),
    ("zeta", "https://api.lever.co/v0/postings/zeta?mode=json"),
    ("groww", "https://api.lever.co/v0/postings/groww?mode=json"),
    ("slice", "https://api.lever.co/v0/postings/slice?mode=json"),
    ("meesho", "https://api.lever.co/v0/postings/meesho?mode=json"),
    ("cars24", "https://api.lever.co/v0/postings/cars24?mode=json"),
    ("unacademy", "https://api.lever.co/v0/postings/unacademy?mode=json"),
    ("zepto", "https://api.lever.co/v0/postings/zepto?mode=json")
]

async def search_interns():
    async with httpx.AsyncClient(timeout=15.0) as client:
        for name, url in BOARDS:
            try:
                r = await client.get(url)
                if r.status_code != 200:
                    continue
                data = r.json()
                raw_jobs = data.get("jobs", []) if isinstance(data, dict) else (data if isinstance(data, list) else [])
                for j in raw_jobs:
                    title = (j.get("title") or j.get("text", "")).lower()
                    loc = ""
                    if isinstance(j.get("location"), dict):
                        loc = j.get("location", {}).get("name", "").lower()
                    elif isinstance(j.get("categories"), dict):
                        loc = j.get("categories", {}).get("location", "").lower()
                    
                    if any(k in title for k in ["intern", "trainee", "campus", "graduate", "early career", "fresher", "associate software", "entry level"]):
                        if any(c in loc for c in ["india", "bangalore", "bengaluru", "hyderabad", "pune", "mumbai", "gurgaon", "noida"]):
                            url_job = j.get("absolute_url") or j.get("hostedUrl") or j.get("url")
                            print(f"FOUND [{name.upper()}]: {j.get('title') or j.get('text')} | Loc: {loc} | URL: {url_job}")
            except Exception as e:
                pass

if __name__ == "__main__":
    asyncio.run(search_interns())
