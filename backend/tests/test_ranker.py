import pytest
from app.pipeline.ranker import RankingEngine

def test_ranker_scoring_and_constraints():
    ranker = RankingEngine()

    candidates = [
        {
            "id": 1,
            "title": "SDE 1",
            "company_slug": "razorpay",
            "company_name": "Razorpay",
            "company_tier": "TIER_1",
            "normalized_city": "Bengaluru",
            "role_category": "SDE",
            "trust_score": 95.0,
            "batch_evidence": "2027 batch",
            "stipend_ctc": "24 LPA"
        },
        {
            "id": 2,
            "title": "Backend Intern",
            "company_slug": "razorpay",
            "company_name": "Razorpay",
            "company_tier": "TIER_1",
            "normalized_city": "Bengaluru",
            "role_category": "Backend",
            "trust_score": 90.0,
            "batch_evidence": "2027 batch",
            "stipend_ctc": "50k pm"
        },
        {
            "id": 3,
            "title": "Frontend Engineer",
            "company_slug": "razorpay", # 3rd from same company!
            "company_name": "Razorpay",
            "company_tier": "TIER_1",
            "normalized_city": "Bengaluru",
            "role_category": "Frontend",
            "trust_score": 88.0,
            "batch_evidence": "2027 batch",
            "stipend_ctc": "20 LPA"
        },
        {
            "id": 4,
            "title": "QA Automation Trainee",
            "company_slug": "inmobi",
            "company_name": "InMobi",
            "company_tier": "TIER_2",
            "normalized_city": "Bengaluru",
            "role_category": "QA/SDET",
            "trust_score": 85.0,
            "batch_evidence": "2027 batch",
            "stipend_ctc": None
        },
        {
            "id": 5,
            "title": "GET Software",
            "company_slug": "tcs",
            "company_name": "TCS",
            "company_tier": "TIER_3",
            "normalized_city": "Hyderabad",
            "role_category": "GET/ASE",
            "trust_score": 82.0,
            "batch_evidence": "2027 batch",
            "stipend_ctc": "7 LPA"
        },
        {
            "id": 6,
            "title": "Data Engineer Intern",
            "company_slug": "postman",
            "company_name": "Postman",
            "company_tier": "TIER_2",
            "normalized_city": "Pune",
            "role_category": "Data Engineer",
            "trust_score": 92.0,
            "batch_evidence": "2027 batch",
            "stipend_ctc": "60k pm"
        }
    ]

    selected = ranker.select_top_jobs("2027", candidates, previously_published_job_ids=set(), target_count=5)

    assert len(selected) <= 5
    # Razorpay must have at most 2 jobs selected
    razorpay_selected = [j for j in selected if j["company_slug"] == "razorpay"]
    assert len(razorpay_selected) <= 2

    # Verify no repeats if job 1 was already published
    selected_without_repeat = ranker.select_top_jobs("2027", candidates, previously_published_job_ids={1}, target_count=5)
    assert 1 not in [j["id"] for j in selected_without_repeat]
