import asyncio
import json
import os
import sys
from datetime import datetime
import click
from sqlalchemy import select, func

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.init_db import init_db
from app.models import Company, Source, Job, RawJob, DailySelection, VerificationResult, JobCohortEligibility
from app.pipeline.daily_runner import DailyPipelineRunner
from app.pipeline.verifier import JobVerifier

@click.group()
def cli():
    """FreshersDaily Command Line Interface"""
    pass

@cli.command("initdb")
def cmd_initdb():
    """Initialize database tables"""
    click.echo("Initializing database tables...")
    asyncio.run(init_db())
    click.echo("Database initialized successfully.")

@cli.command("seed")
@click.option("--companies", is_flag=True, help="Seed 150+ Indian tech companies")
@click.option("--sample-runs", is_flag=True, help="Seed sample verified runs across all 3 cohorts")
def cmd_seed(companies: bool, sample_runs: bool):
    """Seed system data"""
    async def _seed():
        await init_db()
        if companies:
            path = settings.SEED_COMPANIES_PATH
            if not os.path.exists(path):
                click.echo(f"Seed file not found: {path}")
                return
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            async with AsyncSessionLocal() as session:
                added = 0
                for item in data:
                    existing = await session.execute(select(Company).where(Company.slug == item["slug"]))
                    comp = existing.scalar_one_or_none()
                    if not comp:
                        comp = Company(
                            name=item["name"],
                            slug=item["slug"],
                            domain=item["domain"],
                            tier=item.get("tier", "TIER_OTHER"),
                            is_active=True
                        )
                        session.add(comp)
                        await session.flush()
                        added += 1

                    src_existing = await session.execute(
                        select(Source).where(Source.company_id == comp.id, Source.source_type == item["ats_type"])
                    )
                    if not src_existing.scalar_one_or_none():
                        src = Source(
                            company_id=comp.id,
                            source_type=item["ats_type"],
                            base_url=item.get("config", {}).get("base_url"),
                            config_json=json.dumps(item.get("config", {})),
                            is_active=True,
                            status="healthy"
                        )
                        session.add(src)

                await session.commit()
                click.echo(f"Seeded {added} new companies and sources.")

        if sample_runs:
            click.echo("Seeding sample verified runs for 2026, 2027, and 2028 cohorts...")
            from app.pipeline.verifier import JobVerifier
            verifier = JobVerifier()

            sample_jobs = [
                # 2026 Cohort: Full-time entry-level / fresher
                {"comp": "razorpay", "title": "Associate Software Engineer - Frontend", "city": "Bengaluru", "html": "Open to batch of 2026 passouts. B.Tech / B.E. in CSE, IT, ECE. 0-1 years experience. Stipend: 18 LPA CTC.", "url": "https://boards.greenhouse.io/razorpaysoftwareprivatelimited/jobs/5001", "cohort": "2026", "role": "Frontend"},
                {"comp": "postman", "title": "Software Engineer I - Backend APIs", "city": "Bengaluru", "html": "Graduating class of 2026 / 2026 passouts. Strong core fundamentals in Node.js, distributed databases. CTC: 22 LPA.", "url": "https://boards.greenhouse.io/postman/jobs/5002", "cohort": "2026", "role": "Backend"},
                {"comp": "inmobi", "title": "Graduate Engineer Trainee (GET)", "city": "Bengaluru", "html": "Eligible: 2026 batch engineering graduates (B.Tech CSE/IT/ECE). 0 years experience. CTC: 15 LPA.", "url": "https://boards.greenhouse.io/inmobi/jobs/5003", "cohort": "2026", "role": "GET/ASE"},
                {"comp": "cred", "title": "Associate Backend Engineer", "city": "Bengaluru", "html": "Full time entry level role for 2026 passouts. High bar for data structures, algorithms, and system design. CTC: 25 LPA.", "url": "https://jobs.lever.co/cred/5004", "cohort": "2026", "role": "Backend"},
                {"comp": "clevertap", "title": "SDET - Quality Engineering Trainee", "city": "Mumbai", "html": "Open to batch of 2026 freshers. Work on automation test frameworks in Java/Selenium. CTC: 12 LPA.", "url": "https://jobs.lever.co/clevertap/5005", "cohort": "2026", "role": "QA/SDET"},

                # 2027 Cohort: Final year full-time + 6-month Internship with PPO
                {"comp": "uber", "title": "Software Engineering Intern (6 Months + PPO)", "city": "Hyderabad", "html": "Eligible: Students graduating in 2027 (batch of 2027). 6-month internship leading to full-time PPO. Stipend: 1.2 Lakhs/month.", "url": "https://boards.greenhouse.io/uber/jobs/6001", "cohort": "2027", "role": "SDE"},
                {"comp": "atlassian", "title": "Associate Software Engineer - Campus 2027", "city": "Bengaluru", "html": "Target batch: 2027 graduates (final year B.Tech/B.E.). Direct full-time hire starting summer 2027. CTC: 28 LPA.", "url": "https://boards.greenhouse.io/atlassian/jobs/6002", "cohort": "2027", "role": "SDE"},
                {"comp": "stripe", "title": "Backend Engineering Intern (PPO Track)", "city": "Bengaluru", "html": "Looking for students in their final year graduating in 2027. Internship + PPO track. Work on core payment infrastructure.", "url": "https://boards.greenhouse.io/stripe/jobs/6003", "cohort": "2027", "role": "Backend"},
                {"comp": "browserstack", "title": "Fullstack Engineering Intern + PPO", "city": "Mumbai", "html": "Batch of 2027 eligible. 6-month internship with pre-placement offer for full-time. Stipend: 60k pm.", "url": "https://boards.greenhouse.io/browserstack/jobs/6004", "cohort": "2027", "role": "Fullstack"},
                {"comp": "zeta", "title": "Software Development Engineer Trainee - 2027", "city": "Pune", "html": "Open for 2027 graduating batch. Work on high-scale cloud banking microservices. CTC: 16 LPA.", "url": "https://jobs.lever.co/zeta/6005", "cohort": "2027", "role": "SDE"},

                # 2028 Cohort: Pre-final year summer internship / engage / explore programs
                {"comp": "google", "title": "Software Engineering Summer Intern 2026", "city": "Bengaluru", "html": "Pre-final year undergraduate students graduating in 2028. Summer internship program duration 8-10 weeks.", "url": "https://google.myworkdayjobs.com/External/jobs/7001", "cohort": "2028", "role": "SDE"},
                {"comp": "microsoft", "title": "Explore / Summer Internship Program", "city": "Hyderabad", "html": "Designed for students in pre-final year (graduating in 2028). Explore software engineering tracks.", "url": "https://microsoft.myworkdayjobs.com/External/jobs/7002", "cohort": "2028", "role": "SDE"},
                {"comp": "adobe", "title": "Research & Engineering Intern - Summer", "city": "Noida", "html": "Open for pre-final year engineering students graduating in 2028. Work on digital media and machine learning tools.", "url": "https://adobe.myworkdayjobs.com/external_experienced/jobs/7003", "cohort": "2028", "role": "ML/AI"},
                {"comp": "cisco", "title": "Software Engineer Intern - Campus", "city": "Bengaluru", "html": "Summer internship for 2028 batch engineering students (CSE/IT/ECE). Work on networking and cloud security.", "url": "https://cisco.myworkdayjobs.com/Cisco_Careers/jobs/7004", "cohort": "2028", "role": "DevOps/Cloud"},
                {"comp": "salesforce", "title": "Futureforce Tech Intern", "city": "Hyderabad", "html": "Pre-final year students graduating in 2028. Hands-on coding and mentor pairing in cloud platforms.", "url": "https://salesforce.myworkdayjobs.com/External_Career_Site/jobs/7005", "cohort": "2028", "role": "Fullstack"}
            ]

            async with AsyncSessionLocal() as session:
                date_str = datetime.utcnow().strftime("%Y-%m-%d")
                for s in sample_jobs:
                    comp_res = await session.execute(select(Company).where(Company.slug == s["comp"]))
                    comp = comp_res.scalar_one_or_none()
                    if not comp:
                        comp = Company(name=s["comp"].title(), slug=s["comp"], domain=f"{s['comp']}.com", tier="TIER_1")
                        session.add(comp)
                        await session.flush()

                    # Create raw job
                    raw_job = RawJob(
                        source_id=1,
                        external_id=s["url"].split("/")[-1],
                        title=s["title"],
                        location_raw=s["city"],
                        apply_url=s["url"],
                        payload_json=json.dumps({"title": s["title"], "city": s["city"]}),
                        raw_html=s["html"],
                        content_hash=f"hash_{s['comp']}_{s['cohort']}"
                    )
                    session.add(raw_job)
                    await session.flush()

                    # Run verification report
                    report = await verifier.verify_job(
                        title=s["title"],
                        apply_url=s["url"],
                        location_raw=s["city"],
                        raw_html=s["html"],
                        company_domain=comp.domain,
                        skip_network_liveness=True
                    )

                    job = Job(
                        raw_job_id=raw_job.id,
                        company_id=comp.id,
                        title=s["title"],
                        role_category=s["role"],
                        normalized_city=s["city"],
                        country="India",
                        apply_url=s["url"],
                        final_apply_url=s["url"],
                        stipend_ctc=report.extracted_data.stipend_ctc if report.extracted_data else None,
                        stipend_ctc_evidence=report.extracted_data.stipend_ctc_evidence if report.extracted_data else None,
                        trust_score=95.0,
                        status="verified"
                    )
                    session.add(job)
                    await session.flush()

                    session.add(JobCohortEligibility(
                        job_id=job.id,
                        cohort=s["cohort"],
                        role_type=report.extracted_data.role_type if report.extracted_data else "full_time",
                        evidence_snippet=report.extracted_data.batch_evidence or f"Verified batch {s['cohort']}",
                        evidence_url=s["url"],
                        branches="[\"CSE\", \"IT\", \"ECE\"]"
                    ))

                    for vr in report.results:
                        session.add(VerificationResult(
                            job_id=job.id,
                            check_name=vr["check_name"],
                            passed=vr["passed"],
                            score=vr["score"],
                            reason=vr["reason"],
                            evidence_quote=vr.get("evidence_quote")
                        ))

                await session.commit()
                click.echo("Seeded 15 sample verified jobs.")

                # Run daily ranking selection for today
                runner = DailyPipelineRunner(session)
                summary = await runner.run_pipeline(date_str=date_str, dry_run=False, skip_ingest=True)
                click.echo(f"Published sample selections for date {date_str}: 2026={summary['cohort_2026_published']}, 2027={summary['cohort_2027_published']}, 2028={summary['cohort_2028_published']}")

    asyncio.run(_seed())

@cli.command("run-daily")
@click.option("--date", default=None, help="Target date YYYY-MM-DD")
@click.option("--dry-run", is_flag=True, help="Simulate pipeline without saving selections")
@click.option("--skip-ingest", is_flag=True, help="Skip scraping external sources and process existing jobs")
@click.option("--limit-sources", default=None, type=int, help="Limit number of sources for quick run")
def cmd_run_daily(date: str, dry_run: bool, skip_ingest: bool, limit_sources: int):
    """Run ingestion, verification, ranking, and daily publish"""
    async def _run():
        await init_db()
        async with AsyncSessionLocal() as session:
            runner = DailyPipelineRunner(session)
            summary = await runner.run_pipeline(date_str=date, dry_run=dry_run, skip_ingest=skip_ingest, limit_sources=limit_sources)
            click.echo("\n--- DAILY RUN RESULTS ---")
            click.echo(f"Date: {summary['date']}")
            click.echo(f"Dry Run: {summary['dry_run']}")
            click.echo(f"Raw Jobs Ingested: {summary['raw_jobs_ingested']}")
            click.echo(f"Verified: {summary['jobs_verified']} | Needs Review: {summary['jobs_needs_review']} | Rejected: {summary['jobs_rejected']}")
            click.echo(f"Cohort 2026 Selections: {summary['cohort_2026_published']}")
            click.echo(f"Cohort 2027 Selections: {summary['cohort_2027_published']}")
            click.echo(f"Cohort 2028 Selections: {summary['cohort_2028_published']}")
            
            for c, jobs in summary.get("selections", {}).items():
                click.echo(f"\nCohort {c} Top Selections:")
                for idx, j in enumerate(jobs, 1):
                    click.echo(f"  {idx}. {j['title']} @ {j['company_name']} ({j['normalized_city']}) - Score: {j.get('selection_score', 0):.2f}")

    asyncio.run(_run())

@cli.command("verify-url")
@click.option("--url", required=True, help="Job apply URL to verify")
@click.option("--company", default="Direct Employer", help="Company Name")
def cmd_verify_url(url: str, company: str):
    """Manually test a single URL against the 8-stage verification pipeline"""
    async def _verify():
        verifier = JobVerifier()
        report = await verifier.verify_job(
            title="Software Engineer",
            apply_url=url,
            location_raw="India",
            raw_html="",
            company_domain=url,
            skip_network_liveness=False
        )
        click.echo("\n--- VERIFICATION REPORT ---")
        click.echo(f"Status: {report.status.upper()}")
        click.echo(f"Trust Score: {report.final_trust_score}/100")
        click.echo(f"Resolved URL: {report.final_apply_url}")
        click.echo("\nStage Results:")
        for res in report.results:
            mark = "✓" if res["passed"] else "✗"
            click.echo(f"  {mark} {res['check_name']}: {res['reason']}")

    asyncio.run(_verify())

@cli.command("stats")
def cmd_stats():
    """Display system database and verification health statistics"""
    async def _stats():
        async with AsyncSessionLocal() as session:
            comp_count = (await session.execute(select(func.count(Company.id)))).scalar_one()
            src_count = (await session.execute(select(func.count(Source.id)))).scalar_one()
            job_count = (await session.execute(select(func.count(Job.id)))).scalar_one()
            verified_count = (await session.execute(select(func.count(Job.id)).where(Job.status == "verified"))).scalar_one()
            published_count = (await session.execute(select(func.count(Job.id)).where(Job.status == "published"))).scalar_one()
            review_count = (await session.execute(select(func.count(Job.id)).where(Job.status == "needs_review"))).scalar_one()
            rejected_count = (await session.execute(select(func.count(Job.id)).where(Job.status == "rejected"))).scalar_one()

            click.echo("\n--- FRESHERSDAILY PLATFORM STATS ---")
            click.echo(f"Companies: {comp_count}")
            click.echo(f"Sources: {src_count}")
            click.echo(f"Total Jobs: {job_count}")
            click.echo(f"  Published: {published_count}")
            click.echo(f"  Verified: {verified_count}")
            click.echo(f"  Needs Review: {review_count}")
            click.echo(f"  Rejected: {rejected_count}")

    asyncio.run(_stats())

if __name__ == "__main__":
    cli()
