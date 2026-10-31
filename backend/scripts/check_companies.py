import asyncio
import asyncpg

async def main():
    conn = await asyncpg.connect("postgresql://neondb_owner:npg_UPrjoK0VQcb6@ep-noisy-night-b4i7llso-pooler.c-6.us-east-2.aws.neon.tech/neondb?ssl=require")
    companies = await conn.fetch("SELECT id, name, slug, domain FROM companies ORDER BY id;")
    for c in companies:
        print(f"ID: {c['id']} | Name: {c['name']} | Slug: {c['slug']} | Domain: {c['domain']}")
    await conn.close()

asyncio.run(main())
