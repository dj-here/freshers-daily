import asyncio
import asyncpg

async def main():
    conn = await asyncpg.connect("postgresql://neondb_owner:npg_UPrjoK0VQcb6@ep-noisy-night-b4i7llso-pooler.c-6.us-east-2.aws.neon.tech/neondb?ssl=require")
    rows = await conn.fetch("""
        SELECT ds.selection_date, ds.cohort, ds.rank, j.id, c.name, j.title, j.apply_url
        FROM daily_selections ds
        JOIN jobs j ON ds.job_id = j.id
        JOIN companies c ON j.company_id = c.id
        WHERE ds.selection_date IN ('2026-10-30', '2026-10-31')
        ORDER BY ds.selection_date, ds.cohort, ds.rank;
    """)
    for r in rows:
        print(f"[{r['selection_date']}] Cohort {r['cohort']} Rank {r['rank']} | JobID: {r['id']} | Company: {r['name']} | Title: {r['title']} | URL: {r['apply_url']}")
    await conn.close()

asyncio.run(main())
