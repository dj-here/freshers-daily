import asyncio
import json
import re
import httpx

BOARDS = [
    ("Razorpay", "greenhouse", "https://boards-api.greenhouse.io/v1/boards/razorpaysoftwareprivatelimited/jobs?content=true"),
    ("HackerRank", "greenhouse", "https://boards-api.greenhouse.io/v1/boards/hackerrank/jobs?content=true"),
    ("SingleStore", "greenhouse", "https://boards-api.greenhouse.io/v1/boards/singlestore/jobs?content=true"),
    ("Postman", "greenhouse", "https://boards-api.greenhouse.io/v1/boards/postman/jobs?content=true"),
    ("BrowserStack", "greenhouse", "https://boards-api.greenhouse.io/v1/boards/browserstack/jobs?content=true"),
    ("InMobi", "greenhouse", "https://boards-api.greenhouse.io/v1/boards/inmobi/jobs?content=true"),
    ("Sprinklr", "greenhouse", "https://boards-api.greenhouse.io/v1/boards/sprinklr/jobs?content=true"),
    ("Databricks", "greenhouse", "https://boards-api.greenhouse.io/v1/boards/databricks/jobs?content=true"),
    ("MongoDB", "greenhouse", "https://boards-api.greenhouse.io/v1/boards/mongodb/jobs?content=true"),
    ("Cloudflare", "greenhouse", "https://boards-api.greenhouse.io/v1/boards/cloudflare/jobs?content=true"),
    ("Rubrik", "greenhouse", "https://boards-api.greenhouse.io/v1/boards/rubrik/jobs?content=true"),
    ("Stripe", "greenhouse", "https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true"),
    ("Atlassian", "greenhouse", "https://boards-api.greenhouse.io/v1/boards/atlassian/jobs?content=true"),
    ("CRED", "lever", "https://api.lever.co/v0/postings/cred?mode=json"),
    ("CleverTap", "lever", "https://api.lever.co/v0/postings/clevertap?mode=json"),
    ("Zeta", "lever", "https://api.lever.co/v0/postings/zeta?mode=json"),
    ("Meesho", "lever", "https://api.lever.co/v0/postings/meesho?mode=json"),
    ("Groww", "lever", "https://api.lever.co/v0/postings/groww?mode=json"),
    ("Slice", "lever", "https://api.lever.co/v0/postings/slice?mode=json"),
    ("Sarvam AI", "ashby", "https://api.ashbyhq.com/posting-api/job-board/sarvam")
]

INDIA_CITIES = [
    "bengaluru", "bangalore", "hyderabad", "pune", "mumbai", "gurgaon", "gurugram", 
    "noida", "chennai", "delhi", "india", "remote - india"
]

SOFTWARE_KEYWORDS = [
    "software", "engineer", "developer", "backend", "frontend", "fullstack", 
    "full stack", "sde", "intern", "trainee", "qa", "sdet", "devops", "cloud", 
    "data engineer", "machine learning", "ai engineer"
]

EXCLUDE_TITLES = [
    "director", "lead", "principal", "manager", "senior", "sr.", "staff", "head", 
    "sales", "business development", "marketing", "recruiter", "hr", "account executive",
    "operations manager", "legal", "finance"
]

async def scan():
    results = []
    async with httpx.AsyncClient(timeout=15.0) as client:
        for comp_name, ats_type, url in BOARDS:
            try:
                r = await client.get(url)
                if r.status_code != 200:
                    continue
                data = r.json()
                
                raw_jobs = []
                if ats_type == "greenhouse":
                    raw_jobs = data.get("jobs", [])
                elif ats_type == "lever":
                    raw_jobs = data if isinstance(data, list) else []
                elif ats_type == "ashby":
                    raw_jobs = data.get("jobs", [])
                
                for j in raw_jobs:
                    title = j.get("title") or j.get("text", "")
                    title_lower = title.lower()
                    
                    # Check if excluded
                    if any(ex in title_lower for ex in EXCLUDE_TITLES):
                        continue
                        
                    # Check if software
                    if not any(sw in title_lower for sw in SOFTWARE_KEYWORDS):
                        continue
                        
                    # Location check
                    loc = ""
                    if ats_type == "greenhouse":
                        loc = (j.get("location") or {}).get("name", "")
                        apply_url = j.get("absolute_url")
                        content = j.get("content", "")
                        job_id = j.get("id")
                    elif ats_type == "lever":
                        cats = j.get("categories") or {}
                        loc = cats.get("location", "") + " " + cats.get("allLocations", [""])[0] if isinstance(cats.get("allLocations"), list) else cats.get("location", "")
                        apply_url = j.get("hostedUrl")
                        content = j.get("descriptionPlain", "")
                        job_id = j.get("id")
                    elif ats_type == "ashby":
                        loc = j.get("location", "")
                        apply_url = f"https://jobs.ashbyhq.com/sarvam/{j.get('id')}"
                        content = ""
                        job_id = j.get("id")
                        
                    loc_lower = loc.lower()
                    if not any(c in loc_lower for c in INDIA_CITIES):
                        continue
                        
                    results.append({
                        "company": comp_name,
                        "title": title,
                        "location": loc,
                        "apply_url": apply_url,
                        "job_id": job_id,
                        "has_content": len(content) > 50,
                        "content_sample": content[:300].replace("\n", " ") if content else ""
                    })
            except Exception as e:
                print(f"Error on {comp_name}: {e}")

    print(f"Found {len(results)} candidate software jobs in India!")
    with open("scanned_india_software_jobs.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    for item in results:
        print(f"[{item['company']}] {item['title']} ({item['location']}) -> {item['apply_url']}")

if __name__ == "__main__":
    asyncio.run(scan())
