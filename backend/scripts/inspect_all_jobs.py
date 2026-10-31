import asyncio
import asyncpg

async def main():
    conn = await asyncpg.connect("postgresql://neondb_owner:npg_UPrjoK0VQcb6@ep-noisy-night-b4i7llso-pooler.c-6.us-east-2.aws.neon.tech/neondb?ssl=require")
    jobs = await conn.fetch("""
        SELECT j.id, c.name, j.title, j.apply_url, j.status, e.cohort
        FROM jobs j
        JOIN companies c ON j.company_id = c.id
        LEFT JOIN job_cohort_eligibility e ON j.id = e.job_id
        ORDER BY j.id;
    """)
    print(f"Total jobs: {len(jobs)}")
    for j in jobs:
        print(f"ID: {j['id']} | Cohort: {j['cohort']} | {j['name']} | {j['title']} | URL: {j['apply_url']}")
    
    dates = await conn.fetch("SELECT DISTINCT selection_date FROM daily_selections ORDER BY selection_date;")
    print("Distinct selection dates:", [d['selection_date'].isoformat() for d in dates])
    await conn.close()

asyncio.run(main())
