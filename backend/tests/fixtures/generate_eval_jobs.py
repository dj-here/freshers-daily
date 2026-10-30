import json

fixtures = []

# 1-15: Cohort 2026 passouts (already graduated) - full-time roles
for i in range(1, 16):
    fixtures.append({
        "id": f"2026_ft_{i}",
        "title": f"Associate Software Engineer {i}",
        "company": "Tech Corp",
        "location": "Bengaluru, India",
        "content": f"We are looking for fresh engineering graduates for the batch of 2026 passouts. B.Tech / B.E. in Computer Science or IT. Experience: 0-1 years. Stipend/CTC: {8 + (i % 5)} LPA. Work on scalable backend systems.",
        "ground_truth": {
            "eligible_batches": ["2026"],
            "role_type": "full_time",
            "is_valid": True,
            "min_exp": 0.0,
            "max_exp": 1.0
        }
    })

# 16-30: Cohort 2027 graduates (final year) - full-time or internship + PPO
for i in range(1, 16):
    fixtures.append({
        "id": f"2027_ppo_{i}",
        "title": f"Software Engineer Intern (6-Month + PPO) {i}",
        "company": "Fintech Solutions",
        "location": "Hyderabad, Telangana",
        "content": f"Applications open for graduating in 2027 (final year students). 6-month internship with pre-placement offer (PPO) based on performance. B.E/B.Tech in CSE, ECE, EEE. Stipend: {30 + (i % 10)}k pm.",
        "ground_truth": {
            "eligible_batches": ["2027"],
            "role_type": "internship_ppo",
            "is_valid": True,
            "min_exp": 0.0,
            "max_exp": 1.0
        }
    })

# 31-40: Cohort 2028 graduates (pre-final year) - summer internship / engage
for i in range(1, 11):
    fixtures.append({
        "id": f"2028_intern_{i}",
        "title": f"Summer Engineering Intern 2026 {i}",
        "company": "Global Tech",
        "location": "Pune, India",
        "content": f"Summer internship program for pre-final year engineering students graduating in 2028. Duration: 2 months (May - July). 0 years experience required. Work with mentors on distributed storage.",
        "ground_truth": {
            "eligible_batches": ["2028"],
            "role_type": "internship",
            "is_valid": True,
            "min_exp": 0.0,
            "max_exp": 0.0
        }
    })

# 41-44: Experience traps (Seemingly junior title but requires 2-5+ years)
for i in range(1, 5):
    fixtures.append({
        "id": f"exp_trap_{i}",
        "title": f"Software Engineer - Platform {i}",
        "company": "Enterprise Software",
        "location": "Bengaluru, India",
        "content": f"Looking for Software Engineer. Candidate must have minimum 3 to 6 years of hands-on production experience in Java and Kubernetes. Must have led team deliverables.",
        "ground_truth": {
            "eligible_batches": [],
            "role_type": "full_time",
            "is_valid": False, # Trapped!
            "min_exp": 3.0,
            "max_exp": 6.0
        }
    })

# 45-47: Scam postings (Asking fee/deposit)
for i in range(1, 4):
    fixtures.append({
        "id": f"scam_{i}",
        "title": f"Fresher Software Trainee {i}",
        "company": "Quick Career",
        "location": "Noida, India",
        "content": f"Immediate placement for freshers. Candidate must deposit refundable registration fee of Rs 3,500 for training modules and placement certificate.",
        "ground_truth": {
            "eligible_batches": [],
            "role_type": "full_time",
            "is_valid": False,
            "min_exp": 0.0,
            "max_exp": 1.0
        }
    })

# 48-50: Non-software or foreign location
fixtures.append({
    "id": "non_swe_1",
    "title": "Business Development Executive",
    "company": "SalesHub",
    "location": "Mumbai, India",
    "content": "Freshers welcome for B2B client acquisition, lead generation, cold calling and field sales.",
    "ground_truth": {
        "eligible_batches": [],
        "role_type": "full_time",
        "is_valid": False,
        "min_exp": 0.0,
        "max_exp": 1.0
    }
})
fixtures.append({
    "id": "foreign_loc_1",
    "title": "Junior Software Engineer",
    "company": "US Software Inc",
    "location": "Austin, Texas, United States",
    "content": "Graduating class of 2026. Join our core frontend team in Austin office. Must have US work authorization.",
    "ground_truth": {
        "eligible_batches": [],
        "role_type": "full_time",
        "is_valid": False,
        "min_exp": 0.0,
        "max_exp": 1.0
    }
})
fixtures.append({
    "id": "ambiguous_1",
    "title": "Senior Staff Architect",
    "company": "Cloud Systems",
    "location": "Bengaluru, India",
    "content": "Requires 12+ years experience in designing high throughput distributed systems.",
    "ground_truth": {
        "eligible_batches": [],
        "role_type": "full_time",
        "is_valid": False,
        "min_exp": 12.0,
        "max_exp": 15.0
    }
})

print(f"Generated {len(fixtures)} eval fixtures.")
with open("freshers_daily/backend/tests/fixtures/eval_jobs.json", "w", encoding="utf-8") as f:
    json.dump(fixtures, f, indent=2)
print("Saved fixtures/eval_jobs.json successfully.")
