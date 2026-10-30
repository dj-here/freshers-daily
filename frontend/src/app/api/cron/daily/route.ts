import { NextRequest, NextResponse } from "next/server";
import { sql } from "@/lib/db";

export const dynamic = "force-dynamic";

// Vercel Cron Endpoint: Automatically executes every day at 00:00 UTC (05:30 IST)
export async function GET(request: NextRequest) {
  // Check authorization header for CRON_SECRET if configured on Vercel
  const authHeader = request.headers.get("authorization");
  if (
    process.env.CRON_SECRET &&
    authHeader !== `Bearer ${process.env.CRON_SECRET}`
  ) {
    return NextResponse.json({ detail: "Unauthorized cron trigger" }, { status: 401 });
  }

  const today = new Date().toISOString().split("T")[0];

  try {
    // 1. Ensure today's daily selections are published for 2026, 2027, and 2028
    const cohorts = ["2026", "2027", "2028"];
    const results: Record<string, number> = {};

    for (const c of cohorts) {
      // Check if selections already exist for today
      const existing = await sql`
        SELECT count(*) FROM daily_selections 
        WHERE cohort = ${c} AND selection_date = ${today}
      `;

      if (Number(existing[0].count) < 5) {
        // Query top verified jobs eligible for this cohort that haven't been published today
        const candidates = await sql`
          SELECT j.id, j.title, j.trust_score
          FROM jobs j
          JOIN job_cohort_eligibility e ON j.id = e.job_id
          WHERE e.cohort = ${c} 
            AND j.status IN ('verified', 'published')
            AND j.id NOT IN (
              SELECT job_id FROM daily_selections WHERE cohort = ${c}
            )
          ORDER BY j.trust_score DESC, j.id ASC
          LIMIT ${5 - Number(existing[0].count)}
        `;

        let rank = Number(existing[0].count) + 1;
        for (const cand of candidates) {
          await sql`
            INSERT INTO daily_selections (selection_date, cohort, job_id, rank, final_score, selection_explanation, published_at, created_at)
            VALUES (
              ${today}, 
              ${c}, 
              ${cand.id}, 
              ${rank}, 
              0.92, 
              'Automated Vercel cloud cron selection for cohort ' || ${c}, 
              NOW(), 
              NOW()
            )
            ON CONFLICT DO NOTHING
          `;
          rank++;
        }

        // Rotate from pool if needed to ensure exactly 5 verified jobs
        if (rank <= 5) {
          const poolCandidates = await sql`
            SELECT j.id
            FROM jobs j
            JOIN job_cohort_eligibility e ON j.id = e.job_id
            WHERE e.cohort = ${c} 
              AND j.status IN ('verified', 'published')
              AND j.id NOT IN (
                SELECT job_id FROM daily_selections WHERE cohort = ${c} AND selection_date = ${today}
              )
            ORDER BY j.trust_score DESC, j.id ASC
            LIMIT ${6 - rank}
          `;
          for (const cand of poolCandidates) {
            await sql`
              INSERT INTO daily_selections (selection_date, cohort, job_id, rank, final_score, selection_explanation, published_at, created_at)
              VALUES (
                ${today}, 
                ${c}, 
                ${cand.id}, 
                ${rank}, 
                0.93, 
                'Automated re-verified rollover for cohort ' || ${c}, 
                NOW(), 
                NOW()
              )
              ON CONFLICT DO NOTHING
            `;
            rank++;
          }
        }
      }

      const finalCount = await sql`
        SELECT count(*) FROM daily_selections 
        WHERE cohort = ${c} AND selection_date = ${today}
      `;
      results[c] = Number(finalCount[0].count);
    }

    return NextResponse.json({
      success: true,
      message: `Daily publish cron completed successfully for ${today}`,
      date: today,
      cohorts_published: results,
      source: "Vercel Cloud Serverless Cron",
    });
  } catch (error: any) {
    console.error("Cron execution error:", error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
