import asyncio
import asyncpg

async def main():
    conn = await asyncpg.connect("postgresql://neondb_owner:npg_UPrjoK0VQcb6@ep-noisy-night-b4i7llso-pooler.c-6.us-east-2.aws.neon.tech/neondb?ssl=require")
    
    # Check foreign keys on daily_selections
    fks = await conn.fetch("""
        SELECT tc.table_name, kcu.column_name, ccu.table_name AS foreign_table_name, ccu.column_name AS foreign_column_name 
        FROM information_schema.table_constraints AS tc 
        JOIN information_schema.key_column_usage AS kcu ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage AS ccu ON ccu.constraint_name = tc.constraint_name
        WHERE tc.table_name = 'daily_selections';
    """)
    for f in fks:
        print(f)
        
    # Check counts
    ds_count = await conn.fetchval("SELECT COUNT(*) FROM daily_selections;")
    j_count = await conn.fetchval("SELECT COUNT(*) FROM jobs;")
    print(f"daily_selections count: {ds_count}, jobs count: {j_count}")
    
    # Check max job_id
    max_id = await conn.fetchval("SELECT MAX(id) FROM jobs;")
    print(f"Max job id: {max_id}")

    await conn.close()

asyncio.run(main())
