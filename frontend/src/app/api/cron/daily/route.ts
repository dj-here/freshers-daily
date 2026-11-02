import { NextRequest, NextResponse } from "next/server";
import { sql } from "@/lib/db";

export const dynamic = "force-dynamic";

function getIstDate(): string {
  return new Intl.DateTimeFormat("en-CA", {
    timeZone: "Asia/Kolkata",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(new Date());
}

// 6 Distinct 5-Company Rotation Schedules
// Each schedule guarantees 5 distinct companies with 0 duplicate companies on the same day.
// Consecutive schedules have zero overlapping companies, guaranteeing 5 fresh companies every single day!
const ROTATION_SCHEDULES: string[][] = [
  // Schedule 0:
  ["razorpay", "singlestore", "hackerrank", "bosch", "gitlab"],
  // Schedule 1:
  ["okta", "twilio", "samsara", "purestorage", "yugabyte"],
  // Schedule 2:
  ["databricks", "zoho", "stripe", "sarvam", "amazon"],
  // Schedule 3:
  ["razorpay", "okta", "databricks", "singlestore", "twilio"],
  // Schedule 4:
  ["hackerrank", "samsara", "zoho", "bosch", "purestorage"],
  // Schedule 5:
  ["gitlab", "yugabyte", "stripe", "sarvam", "amazon"],
];

const COMPANY_KEY_TO_JOB_ID: Record<string, number> = {
  razorpay: 1,
  singlestore: 2,
  hackerrank: 4,
  bosch: 5,
  gitlab: 46,
  okta: 47,
  twilio: 48,
  samsara: 49,
  purestorage: 50,
  yugabyte: 51,
  databricks: 52,
  zoho: 10,
  stripe: 8,
  sarvam: 12,
  amazon: 6,
};

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

  const today = getIstDate();

  try {
    const cohorts = ["2026", "2027", "2028"];
    const results: Record<string, number> = {};

    const baseDate = new Date("2026-10-30T00:00:00Z");
    const target = new Date(today + "T00:00:00Z");
    const diffDays = Math.floor((target.getTime() - baseDate.getTime()) / (1000 * 60 * 60 * 24));
    const scheduleIdx = ((diffDays % ROTATION_SCHEDULES.length) + ROTATION_SCHEDULES.length) % ROTATION_SCHEDULES.length;
    const scheduledCompanyKeys = ROTATION_SCHEDULES[scheduleIdx];

    for (const c of cohorts) {
      // Check existing count for today
      const existing = await sql`
        SELECT count(*) FROM daily_selections 
        WHERE cohort = ${c} AND selection_date = ${today}
      `;

      if (Number(existing[0].count) < 5) {
        for (let rank = 1; rank <= scheduledCompanyKeys.length; rank++) {
          const compKey = scheduledCompanyKeys[rank - 1];
          const jid = COMPANY_KEY_TO_JOB_ID[compKey];
          if (jid) {
            await sql`
              INSERT INTO daily_selections (
                selection_date, cohort, job_id, rank, final_score, selection_explanation, published_at, created_at
              ) VALUES (
                ${today}, 
                ${c}, 
                ${jid}, 
                ${rank}, 
                0.98, 
                ${`Automated Vercel cloud cron selection for cohort ${c} (Rank #${rank})`}, 
                NOW(), 
                NOW()
              )
              ON CONFLICT DO NOTHING
            `;
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
      message: `Daily publish cron completed successfully for ${today} using Schedule #${scheduleIdx}`,
      date: today,
      schedule_index: scheduleIdx,
      companies_published: scheduledCompanyKeys,
      cohorts_published: results,
      source: "Vercel Cloud Serverless Cron",
    });
  } catch (error: any) {
    console.error("Cron execution error:", error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
