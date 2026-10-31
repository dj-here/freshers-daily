import asyncio
import httpx
from bs4 import BeautifulSoup

URLS = [
    # Cohort 2026:
    ("2026", "Razorpay", "AI Builder (Engineering Trainee)", "https://job-boards.greenhouse.io/razorpaysoftwareprivatelimited/jobs/4744950005"),
    ("2026", "SingleStore", "Software Engineer (University Graduate Track)", "https://job-boards.greenhouse.io/singlestore/jobs/8212128"),
    ("2026", "SingleStore", "Software Engineer | Database Engine", "https://job-boards.greenhouse.io/singlestore/jobs/8000966"),
    ("2026", "HackerRank", "Customer Experience Engineer, L1", "https://job-boards.greenhouse.io/hackerrank/jobs/8127535"),
    ("2026", "Bosch Group", "CRM Junior Engineer with DevOps", "https://jobs.smartrecruiters.com/BoschGroup/744000156714729"),
    ("2026", "SingleStore", "Support Engineer (Systems & Cloud)", "https://job-boards.greenhouse.io/singlestore/jobs/8267309"),

    # Cohort 2027:
    ("2027", "Amazon", "SDE I Intern (Amazon University Talent Acquisition)", "https://www.amazon.jobs/en/jobs/10572995/sde-i-intern-amazon-university-talent-acquisition"),
    ("2027", "Amazon", "SDE I Intern (India Talent Acquisition Pipeline)", "https://www.amazon.jobs/en/jobs/10541345/sde-i-intern-amazon-university-talent-acquisition"),
    ("2027", "HackerRank", "Software Development Engineer Intern (PPO Track)", "https://job-boards.greenhouse.io/hackerrank/jobs/8229735"),
    ("2027", "Stripe", "Software Engineer, New Grad (Class of 2027)", "https://job-boards.greenhouse.io/stripe/jobs/8130876"),
    ("2027", "Zoho Corporation", "Software Developer Trainee (Off-Campus Drive)", "https://careers.zohocorp.com/candidateportal?register=true"),

    # Cohort 2028:
    ("2028", "Stripe", "Software Engineer, Intern (Summer Program)", "https://job-boards.greenhouse.io/stripe/jobs/8031833"),
    ("2028", "HackerRank", "AI Researcher Intern (Pre-Final Year)", "https://job-boards.greenhouse.io/hackerrank/jobs/8281055"),
    ("2028", "SingleStore", "Cloud Platform Engineer", "https://job-boards.greenhouse.io/singlestore/jobs/8212152"),
    ("2028", "Sarvam AI", "Frontend Engineer (Foundational Voice & GenAI Platforms)", "https://jobs.ashbyhq.com/sarvam/10a352d0-a65b-4599-8998-e09deef34349"),
    ("2028", "Sarvam AI", "Software Engineer - Model API Platform", "https://jobs.ashbyhq.com/sarvam/0371342b-5cb8-487b-9310-4d0eb5b37f47"),
]

async def check():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    async with httpx.AsyncClient(headers=headers, timeout=12.0, follow_redirects=True) as client:
        for cohort, company, title, url in URLS:
            try:
                r = await client.get(url)
                soup = BeautifulSoup(r.text, "html.parser")
                page_title = soup.title.string.strip() if soup.title and soup.title.string else ""
                text = soup.get_text(separator=" ", strip=True).lower()
                is_closed = any(k in text for k in ["no longer available", "position closed", "job not found", "404"])
                has_apply = any(k in text for k in ["apply", "resume", "first name", "candidate portal", "register"])
                print(f"[{cohort}] {company} - {title}: Status {r.status_code} | Closed: {is_closed} | Has Apply: {has_apply} | Title: {page_title[:40]} | URL: {url}", flush=True)
            except Exception as e:
                print(f"[{cohort}] {company} ERROR: {e}", flush=True)

if __name__ == "__main__":
    asyncio.run(check())
