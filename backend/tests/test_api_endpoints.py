import pytest
import httpx
from app.main import app

@pytest.mark.asyncio
async def test_api_cohorts_daily():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Test Cohort 2027
        resp2027 = await client.get("/api/v1/cohorts/2027/daily")
        assert resp2027.status_code == 200
        data2027 = resp2027.json()
        assert data2027["cohort"] == "2027"
        assert len(data2027["today_openings"]) == 5
        first_job = data2027["today_openings"][0]["job"]
        assert first_job["status"] in ("published", "verified")
        assert len(first_job["cohort_eligibilities"]) > 0
        assert first_job["cohort_eligibilities"][0]["evidence_snippet"] is not None

        # Test Cohort 2026
        resp2026 = await client.get("/api/v1/cohorts/2026/daily")
        assert resp2026.status_code == 200
        data2026 = resp2026.json()
        assert data2026["cohort"] == "2026"
        assert len(data2026["today_openings"]) == 5

        # Test Cohort 2028
        resp2028 = await client.get("/api/v1/cohorts/2028/daily")
        assert resp2028.status_code == 200
        data2028 = resp2028.json()
        assert data2028["cohort"] == "2028"
        assert len(data2028["today_openings"]) == 5

@pytest.mark.asyncio
async def test_api_health():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert data["database"]["companies"] >= 150
        assert data["database"]["published"] >= 15

@pytest.mark.asyncio
async def test_api_rss_feed():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/feed/2027.xml")
        assert resp.status_code == 200
        assert "<rss version=\"2.0\">" in resp.text
        assert "FreshersDaily - Cohort 2027" in resp.text

@pytest.mark.asyncio
async def test_api_subscribe():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/subscriptions",
            json={"email": "student2027@example.com", "cohort": "2027"}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["cohort"] == "2027"
