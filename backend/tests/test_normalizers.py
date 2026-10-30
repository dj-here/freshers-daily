import pytest
from app.pipeline.normalizers import normalize_location, classify_role_category

def test_normalize_location_indian_cities():
    res1 = normalize_location("Bengaluru, Karnataka, India")
    assert res1.is_valid_india is True
    assert res1.city == "Bengaluru"
    assert res1.state == "Karnataka"

    res2 = normalize_location("Bangalore Urban")
    assert res2.is_valid_india is True
    assert res2.city == "Bengaluru"

    res3 = normalize_location("Hyderabad, Telangana")
    assert res3.is_valid_india is True
    assert res3.city == "Hyderabad"

    res4 = normalize_location("Pune, MH")
    assert res4.is_valid_india is True
    assert res4.city == "Pune"

    res5 = normalize_location("Gurgaon / Gurugram, Haryana")
    assert res5.is_valid_india is True
    assert res5.city == "Gurgaon"

    res6 = normalize_location("Remote - India")
    assert res6.is_valid_india is True
    assert res6.is_remote is True
    assert "India" in res6.city

def test_normalize_location_foreign_rejection():
    res1 = normalize_location("San Francisco, CA, United States")
    assert res1.is_valid_india is False
    assert "Foreign location" in (res1.rejection_reason or "")

    res2 = normalize_location("London, UK")
    assert res2.is_valid_india is False

    res3 = normalize_location("Berlin, Germany")
    assert res3.is_valid_india is False

    res4 = normalize_location("Singapore")
    assert res4.is_valid_india is False

    res5 = normalize_location("Warsaw, Poland")
    assert res5.is_valid_india is False

def test_classify_role_category_valid_software():
    cat1, conf1 = classify_role_category("Software Development Engineer I (SDE 1)")
    assert cat1 == "SDE"
    assert conf1 >= 0.80

    cat2, conf2 = classify_role_category("Backend Developer - Python / Django")
    assert cat2 == "Backend"
    assert conf2 >= 0.80

    cat3, conf3 = classify_role_category("React Frontend Engineer")
    assert cat3 == "Frontend"
    assert conf3 >= 0.80

    cat4, conf4 = classify_role_category("Full Stack Developer")
    assert cat4 == "Fullstack"
    assert conf4 >= 0.80

    cat5, conf5 = classify_role_category("QA Automation Engineer (SDET)")
    assert cat5 == "QA/SDET"
    assert conf5 >= 0.80

    cat6, conf6 = classify_role_category("Graduate Engineer Trainee - 2026 Batch")
    assert cat6 == "GET/ASE"
    assert conf6 >= 0.80

def test_classify_role_category_non_software_rejection():
    cat1, conf1 = classify_role_category("Business Development Executive (BDE)")
    assert cat1 == "NON_SOFTWARE"
    assert conf1 == 0.0

    cat2, conf2 = classify_role_category("HR Recruiter")
    assert cat2 == "NON_SOFTWARE"
    assert conf2 == 0.0

    cat3, conf3 = classify_role_category("Customer Support Associate")
    assert cat3 == "NON_SOFTWARE"
    assert conf3 == 0.0
