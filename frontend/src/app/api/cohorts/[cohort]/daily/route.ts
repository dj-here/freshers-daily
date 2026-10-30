import { NextRequest, NextResponse } from "next/server";
import { sql } from "@/lib/db";

export const dynamic = "force-dynamic";

export async function GET(
  request: NextRequest,
  { params }: { params: { cohort: string } }
) {
  const cohort = params.cohort;
  if (!["2026", "2027", "2028"].includes(cohort)) {
    return NextResponse.json({ error: "Invalid cohort" }, { status: 400 });
  }

  const { searchParams } = new URL(request.url);
  const targetDate = searchParams.get("date") || new Date().toISOString().split("T")[0];

  try {
    // 1. Fetch daily selections for target date from Neon
    const selections = await sql`
      SELECT 
        ds.id as ds_id,
        ds.selection_date,
        ds.cohort,
        ds.rank,
        ds.final_score,
        ds.selection_explanation,
        ds.published_at,
        j.id as job_id,
        j.title,
        j.role_category,
        j.normalized_city,
        j.state,
        j.country,
        j.is_remote,
        j.is_hybrid,
        j.apply_url,
        j.final_apply_url,
        j.stipend_ctc,
        j.stipend_ctc_evidence,
        j.deadline,
        j.deadline_evidence,
        j.trust_score,
        j.status,
        j.created_at as job_created_at,
        c.name as company_name,
        c.slug as company_slug,
        c.tier as company_tier,
        c.domain as company_domain
      FROM daily_selections ds
      JOIN jobs j ON ds.job_id = j.id
      JOIN companies c ON j.company_id = c.id
      WHERE ds.cohort = ${cohort} AND ds.selection_date = ${targetDate}
      ORDER BY ds.rank ASC
    `;

    // Helper to fetch details
    const enrichSelections = async (rawList: any[]) => {
      const enriched = [];
      for (const row of rawList) {
        const eligibilities = await sql`
          SELECT id, cohort, role_type, evidence_snippet, evidence_url, min_exp_years, max_exp_years, branches, degree_requirements
          FROM job_cohort_eligibility
          WHERE job_id = ${row.job_id}
        `;

        const verificationResults = await sql`
          SELECT id, check_name, passed, score, reason, evidence_quote, checked_at
          FROM verification_results
          WHERE job_id = ${row.job_id}
        `;

        enriched.push({
          id: row.ds_id,
          selection_date: row.selection_date,
          cohort: row.cohort,
          rank: row.rank,
          final_score: Number(row.final_score),
          selection_explanation: row.selection_explanation,
          published_at: row.published_at,
          job: {
            id: row.job_id,
            company_name: row.company_name,
            company_slug: row.company_slug,
            company_tier: row.company_tier,
            company_domain: row.company_domain,
            title: row.title,
            role_category: row.role_category,
            normalized_city: row.normalized_city,
            state: row.state,
            country: row.country,
            is_remote: Boolean(row.is_remote),
            is_hybrid: Boolean(row.is_hybrid),
            apply_url: row.apply_url,
            final_apply_url: row.final_apply_url || row.apply_url,
            stipend_ctc: row.stipend_ctc,
            stipend_ctc_evidence: row.stipend_ctc_evidence,
            deadline: row.deadline,
            deadline_evidence: row.deadline_evidence,
            trust_score: Number(row.trust_score),
            status: row.status,
            created_at: row.job_created_at,
            cohort_eligibilities: eligibilities,
            verification_results: verificationResults,
          },
        });
      }
      return enriched;
    }

    const todayOpenings = await enrichSelections(selections);
    const count = todayOpenings.length;
    const isComplete = count >= 5;
    let message: string | null = null;
    let stillOpenFallback: any[] = [];

    // Fallback if fewer than 5 pass today
    if (count < 5) {
      message = `Only ${count} verified opening${count !== 1 ? "s" : ""} found today. Showing still-open verified opportunities from previous days below.`;
      const selectedJobIds = todayOpenings.map((o) => o.job.id);

      const fallbackSelections = await sql`
        SELECT 
          ds.id as ds_id,
          ds.selection_date,
          ds.cohort,
          ds.rank,
          ds.final_score,
          ds.selection_explanation,
          ds.published_at,
          j.id as job_id,
          j.title,
          j.role_category,
          j.normalized_city,
          j.state,
          j.country,
          j.is_remote,
          j.is_hybrid,
          j.apply_url,
          j.final_apply_url,
          j.stipend_ctc,
          j.stipend_ctc_evidence,
          j.deadline,
          j.deadline_evidence,
          j.trust_score,
          j.status,
          j.created_at as job_created_at,
          c.name as company_name,
          c.slug as company_slug,
          c.tier as company_tier,
          c.domain as company_domain
        FROM daily_selections ds
        JOIN jobs j ON ds.job_id = j.id
        JOIN companies c ON j.company_id = c.id
        WHERE ds.cohort = ${cohort} 
          AND ds.selection_date < ${targetDate}
        ORDER BY ds.selection_date DESC, ds.rank ASC
        LIMIT ${5 - count}
      `;
      stillOpenFallback = await enrichSelections(fallbackSelections);
    }

    return NextResponse.json(
      {
        date: targetDate,
        cohort,
        verified_count: count,
        is_complete: isComplete,
        message,
        today_openings: todayOpenings,
        still_open_fallback: stillOpenFallback,
      },
      {
        headers: {
          "Cache-Control": "public, s-maxage=60, stale-while-revalidate=300",
        },
      }
    );
  } catch (error: any) {
    console.error("API error fetching daily feed from Neon:", error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
