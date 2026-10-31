import asyncio
import json
import re
import httpx
from bs4 import BeautifulSoup

# We test specific candidate job postings
CANDIDATES = [
    # Cohort 2026: 0-1 yrs exp, entry level, freshers, graduate engineer trainees
    {
        "cohort": "2026",
        "company": "Razorpay",
        "title": "AI Builder (Engineering Trainee)",
        "url": "https://job-boards.greenhouse.io/razorpaysoftwareprivatelimited/jobs/4744950005",
        "city": "Bengaluru",
        "role": "Backend"
    },
    {
        "cohort": "2026",
        "company": "SingleStore",
        "title": "Software Engineer (University Graduate Track)",
        "url": "https://job-boards.greenhouse.io/singlestore/jobs/8212128",
        "city": "Bengaluru",
        "role": "SDE"
    },
    {
        "cohort": "2026",
        "company": "SingleStore",
        "title": "Software Engineer | Database Engine",
        "url": "https://job-boards.greenhouse.io/singlestore/jobs/8000966",
        "city": "Bengaluru",
        "role": "SDE"
    },
    {
        "cohort": "2026",
        "company": "SingleStore",
        "title": "Support Engineer (Cloud & Systems)",
        "url": "https://job-boards.greenhouse.io/singlestore/jobs/8267309",
        "city": "Bengaluru",
        "role": "DevOps/Cloud"
    },
    {
        "cohort": "2026",
        "company": "HackerRank",
        "title": "Customer Experience Engineer, L1",
        "url": "https://job-boards.greenhouse.io/hackerrank/jobs/8127535",
        "city": "Bengaluru",
        "role": "Fullstack"
    },
    {
        "cohort": "2026",
        "company": "Bosch Group",
        "title": "CRM Junior Engineer with DevOps",
        "url": "https://jobs.smartrecruiters.com/BoschGroup/744000156714729",
        "city": "Bengaluru",
        "role": "DevOps/Cloud"
    },

    # Cohort 2027: 2027 Graduating Batch (Final Year / 6-Month Intern + PPO / New Grad)
    {
        "cohort": "2027",
        "company": "Amazon",
        "title": "SDE I Intern (India Talent Acquisition Pipeline)",
        "url": "https://www.amazon.jobs/en/jobs/10541345/sde-i-intern-amazon-university-talent-acquisition",
        "city": "Bengaluru",
        "role": "SDE"
    },
    {
        "cohort": "2027",
        "company": "Amazon",
        "title": "SDE I Intern (Amazon University Talent Acquisition)",
        "url": "https://www.amazon.jobs/en/jobs/10572995/sde-i-intern-amazon-university-talent-acquisition",
        "city": "Bengaluru",
        "role": "SDE"
    },
    {
        "cohort": "2027",
        "company": "HackerRank",
        "title": "Software Development Engineer Intern (PPO Track)",
        "url": "https://job-boards.greenhouse.io/hackerrank/jobs/8229735",
        "city": "Bengaluru",
        "role": "SDE"
    },
    {
        "cohort": "2027",
        "company": "Stripe",
        "title": "Software Engineer, New Grad (Class of 2027)",
        "url": "https://stripe.com/jobs/search?gh_jid=8130876",
        "city": "Bengaluru",
        "role": "Backend"
    },
    {
        "cohort": "2027",
        "company": "Zoho Corporation",
        "title": "Software Developer Trainee (Off-Campus 2027 Drive)",
        "url": "https://careers.zohocorp.com/candidateportal?register=true",
        "city": "Chennai",
        "role": "SDE"
    },

    # Cohort 2028: 2028 Graduating Batch (Pre-Final Year / Summer Internships & Early Explore)
    {
        "cohort": "2028",
        "company": "Stripe",
        "title": "Software Engineer, Intern (Summer Program)",
        "url": "https://stripe.com/jobs/search?gh_jid=8031833",
        "city": "Bengaluru",
        "role": "Backend"
    },
    {
        "cohort": "2028",
        "company": "HackerRank",
        "title": "AI Researcher Intern (Pre-Final Year)",
        "url": "https://job-boards.greenhouse.io/hackerrank/jobs/8281055",
        "city": "Bengaluru",
        "role": "ML/AI"
    },
    {
        "cohort": "2028",
        "company": "Rubrik",
        "title": "ENG Project & Systems Intern",
        "url": "https://www.rubrik.com/company/careers/departments/job.8166514?gh_jid=8166514",
        "city": "Bengaluru",
        "role": "SDE"
    },
    {
        "cohort": "2028",
        "company": "Sarvam AI",
        "title": "Frontend Engineer (Foundational Voice & GenAI Platforms)",
        "url": "https://jobs.ashbyhq.com/sarvam/10a352d0-a65b-4599-8998-e09deef34349",
        "city": "Bengaluru",
        "role": "Frontend"
    },
    {
        "cohort": "2028",
        "company": "Sarvam AI",
        "title": "Software Engineer - Model API Platform",
        "url": "https://jobs.ashbyhq.com/sarvam/0371342b-5cb8-487b-9310-4d0eb5b37f47",
        "city": "Bengaluru",
        "role": "Backend"
    }
]

async def check():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    async with httpx.AsyncClient(headers=headers, timeout=12.0, follow_redirects=True) as client:
        for c in CANDIDATES:
            try:
                r = await client.get(c["url"])
                soup = BeautifulSoup(r.text, "html.parser")
                text = soup.get_text(separator=" ", strip=True).lower()
                
                is_closed = any(k in text for k in ["no longer available", "position closed", "job not found", "expired"])
                has_apply = any(k in text for k in ["apply", "first name", "resume", "submit application", "attach resume", "candidate portal"])
                
                print(f"[{c['cohort']}] {c['company']} - {c['title']}")
                print(f"   Status: {r.status_code} | Closed: {is_closed} | Has Apply Form: {has_apply}")
                print(f"   Resolved URL: {r.url}")
                print("--------------------------------------------------")
            except Exception as e:
                print(f"[{c['cohort']}] {c['company']} ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(check())
