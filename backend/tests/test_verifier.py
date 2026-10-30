import pytest
from app.pipeline.verifier import JobVerifier

@pytest.mark.asyncio
async def test_domain_trust_known_ats():
    verifier = JobVerifier()
    
    # Valid Greenhouse URL
    res1, reason1, _ = verifier._check_domain_trust("https://boards.greenhouse.io/razorpay/jobs/12345", "razorpay.com")
    assert res1 is True

    # Valid Lever URL
    res2, reason2, _ = verifier._check_domain_trust("https://jobs.lever.co/cred/abcdef", "cred.club")
    assert res2 is True

    # Disallowed URL Shortener
    res3, reason3, _ = verifier._check_domain_trust("https://bit.ly/3xyzJob", "company.com")
    assert res3 is False
    assert "disallowed" in reason3.lower()

    # Disallowed Google Forms
    res4, reason4, _ = verifier._check_domain_trust("https://docs.google.com/forms/d/e/xyz/viewform", "company.com")
    assert res4 is False

@pytest.mark.asyncio
async def test_scam_keyword_detection():
    verifier = JobVerifier()

    scam_text = "Pay refundable security deposit of Rs 2000 to complete registration."
    p1, r1 = verifier._check_scam(scam_text)
    assert p1 is False
    assert "Scam phrase" in r1

    clean_text = "We are hiring Software Engineers for our Bengaluru tech center."
    p2, r2 = verifier._check_scam(clean_text)
    assert p2 is True

@pytest.mark.asyncio
async def test_experience_trap_rejection():
    verifier = JobVerifier()
    
    # 2+ years experience trap in a seemingly entry-level titled job
    report = await verifier.verify_job(
        title="Software Engineer I",
        apply_url="https://boards.greenhouse.io/test/jobs/1",
        location_raw="Bengaluru",
        raw_html="Minimum 3 to 5 years of professional software engineering experience required.",
        company_domain="test.com",
        skip_network_liveness=True
    )
    assert report.status == "rejected"
    assert any("experience" in r.lower() for r in report.rejection_reasons)

@pytest.mark.asyncio
async def test_fresher_valid_job_acceptance():
    verifier = JobVerifier()

    report = await verifier.verify_job(
        title="Associate Software Engineer - 2026 Batch",
        apply_url="https://boards.greenhouse.io/test/jobs/2",
        location_raw="Pune, India",
        raw_html="Open for 2026 passouts. B.Tech in CSE / IT with 0-1 years of experience. Stipend: 45k pm.",
        company_domain="test.com",
        skip_network_liveness=True
    )
    assert report.status == "verified"
    assert report.final_trust_score >= 80.0
    assert "2026" in report.extracted_data.eligible_batches
