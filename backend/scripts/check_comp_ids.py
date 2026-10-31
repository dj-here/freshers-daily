import asyncio
import asyncpg

async def main():
    conn = await asyncpg.connect("postgresql://neondb_owner:npg_UPrjoK0VQcb6@ep-noisy-night-b4i7llso-pooler.c-6.us-east-2.aws.neon.tech/neondb?ssl=require")
    rows = await conn.fetch("SELECT id, name FROM companies WHERE name ILIKE ANY($1);", ['%SingleStore%', '%Bosch%', '%HackerRank%', '%Amazon%', '%Stripe%', '%Zoho%', '%Sarvam%', '%Razorpay%'])
    for r in rows:
        print(r)
    await conn.close()

asyncio.run(main())
