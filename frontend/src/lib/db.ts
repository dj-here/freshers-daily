import { Pool, neon } from "@neondatabase/serverless";

// Neon Cloud Serverless Database URL with Connection Pooling
const connectionString =
  process.env.DATABASE_URL ||
  "postgresql://neondb_owner:npg_UPrjoK0VQcb6@ep-noisy-night-b4i7llso-pooler.c-6.us-east-2.aws.neon.tech/neondb?sslmode=require";

// Clean any asyncpg prefixes if passed from python envs
const cleanConnectionString = connectionString.replace("postgresql+asyncpg://", "postgresql://");

export const sql = neon(cleanConnectionString);
export const pool = new Pool({ connectionString: cleanConnectionString });
