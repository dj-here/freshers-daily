import asyncio
import asyncpg

async def main():
    conn = await asyncpg.connect("postgresql://neondb_owner:npg_UPrjoK0VQcb6@ep-noisy-night-b4i7llso-pooler.c-6.us-east-2.aws.neon.tech/neondb?ssl=require")
    r = await conn.fetch("SELECT id, raw_job_id, title FROM jobs ORDER BY id LIMIT 10;")
    for row in r:
        print(row)
    raw_max = await conn.fetchval("SELECT MAX(id) FROM raw_jobs;")
    print("raw_jobs max id:", raw_max)
    await conn.close()

asyncio.run(main())
