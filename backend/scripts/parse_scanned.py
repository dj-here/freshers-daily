import json

with open("scanned_india_software_jobs.json", "r", encoding="utf-8") as f:
    jobs = json.load(f)

print(f"Total scanned: {len(jobs)}")
for idx, j in enumerate(jobs):
    print(f"{idx+1}. [{j['company']}] {j['title']} ({j['location']})")
    print(f"   URL: {j['apply_url']}")
