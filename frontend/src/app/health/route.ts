import { NextResponse } from "next/server";
import { sql } from "@/lib/db";

export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const compCount = (await sql`SELECT count(*) FROM companies`)[0].count;
    const srcCount = (await sql`SELECT count(*) FROM sources`)[0].count;
    const jobCount = (await sql`SELECT count(*) FROM jobs`)[0].count;
    const pubCount = (await sql`SELECT count(*) FROM daily_selections`)[0].count;

    return NextResponse.json({
      status: "healthy",
      app: "FreshersDaily",
      platform: "Vercel Edge / Serverless",
      database: "Neon Cloud Serverless PostgreSQL",
      metrics: {
        companies: Number(compCount),
        sources: Number(srcCount),
        jobs_total: Number(jobCount),
        daily_published_selections: Number(pubCount),
      },
    });
  } catch (error: any) {
    return NextResponse.json(
      { status: "unhealthy", error: error.message },
      { status: 500 }
    );
  }
}
