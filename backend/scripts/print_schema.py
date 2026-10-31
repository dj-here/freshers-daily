import asyncio
import asyncpg

async def main():
    conn = await asyncpg.connect("postgresql://neondb_owner:npg_UPrjoK0VQcb6@ep-noisy-night-b4i7llso-pooler.c-6.us-east-2.aws.neon.tech/neondb?ssl=require")
    for tbl in ['job_cohort_eligibility', 'verification_results', 'jobs', 'daily_selections']:
        cols = await conn.fetch("SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = $1;", tbl)
        print(f"--- {tbl} ---")
        for c in cols:
            print(f"  {c['column_name']} ({c['data_type']}, nullable={c['is_nullable']})")
    await conn.close()

asyncio.run(main())
