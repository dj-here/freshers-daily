import json
import re

with open("greenhouse_india_all.json", "r", encoding="utf-8") as f:
    jobs = json.load(f)

print(f"Total: {len(jobs)}")

SOFTWARE_KEYWORDS = [
    "software engineer", "developer", "backend", "frontend", "fullstack", 
    "full stack", "intern", "trainee", "sde", "qa", "sdet", "devops", "cloud",
    "data engineer", "systems engineer", "associate engineer", "ai engineer"
]

EXCLUDE = [
    "senior", "sr.", "principal", "lead", "manager", "director", "head", 
    "staff", "account", "sales", "marketing", "recruiter", "hr", "analyst, otc",
    "legal", "payroll", "finance", "tax", "facilities", "security architect"
]

qualified = []
for j in jobs:
    t = j["title"].lower()
    if any(ex in t for ex in EXCLUDE):
        continue
    if any(sw in t for sw in SOFTWARE_KEYWORDS):
        qualified.append(j)

print(f"Qualified software roles: {len(qualified)}")
for q in qualified:
    print(f"[{q['board']}] {q['title']} ({q['location']}) -> {q['url']}")

with open("qualified_gh_software_india.json", "w", encoding="utf-8") as f:
    json.dump(qualified, f, indent=2)
