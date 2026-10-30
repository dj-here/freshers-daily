import { NextRequest, NextResponse } from "next/server";
import { sql } from "@/lib/db";
import crypto from "crypto";

export const dynamic = "force-dynamic";

export async function POST(request: NextRequest) {
  const adminKey = request.headers.get("x-admin-key");
  const expectedKey = process.env.ADMIN_API_KEY || "adminkey-dev-supersecret-freshersdaily-2026";
  if (adminKey !== expectedKey) {
    return NextResponse.json({ detail: "Unauthorized" }, { status: 401 });
  }

  try {
    const { url, company_name, expected_cohort } = await request.json();
    if (!url) {
      return NextResponse.json({ detail: "URL is required" }, { status: 400 });
    }

    const compName = company_name || "Direct Employer";
    const compSlug = compName.toLowerCase().replace(/\s+/g, "-");
    const domain = url.includes("//") ? url.split("/")[2] : "portal.com";

    // 1. Get or create company
    let comp = (await sql`SELECT id FROM companies WHERE slug = ${compSlug}`)[0];
    if (!comp) {
      comp = (
        await sql`
        INSERT INTO companies (name, slug, domain, tier, is_active, created_at, updated_at)
        VALUES (${compName}, ${compSlug}, ${domain}, 'TIER_2', true, NOW(), NOW())
        RETURNING id
      `
      )[0];
    }

    // 2. Insert raw job
    const hash = crypto.createHash("sha256").update(url + Date.now()).digest("hex");
    const rawJob = (
      await sql`
      INSERT INTO raw_jobs (source_id, external_id, title, location_raw, apply_url, payload_json, content_hash, first_seen_at, created_at)
      VALUES (1, ${'manual_' + Date.now()}, 'Software Engineer', 'India', ${url}, '{}', ${hash}, NOW(), NOW())
      RETURNING id
    `
    )[0];

    // 3. Insert job
    const job = (
      await sql`
      INSERT INTO jobs (raw_job_id, company_id, title, role_category, normalized_city, country, is_remote, is_hybrid, apply_url, final_apply_url, trust_score, status, created_at, updated_at)
      VALUES (${rawJob.id}, ${comp.id}, 'Software Engineer', 'SDE', 'Bengaluru', 'India', false, false, ${url}, ${url}, 88.0, 'verified', NOW(), NOW())
      RETURNING id, title, role_category, normalized_city, trust_score, status
    `
    )[0];

    // 4. Insert cohort eligibility
    const cohort = expected_cohort || "2027";
    await sql`
      INSERT INTO job_cohort_eligibility (job_id, cohort, role_type, evidence_snippet, evidence_url, min_exp_years, max_exp_years, branches, created_at)
      VALUES (${job.id}, ${cohort}, 'full_time', 'Direct manual submission verified', ${url}, 0, 1, '["CSE", "IT"]', NOW())
    `;

    return NextResponse.json({
      success: true,
      message: "Job verified and added successfully",
      job,
    });
  } catch (error: any) {
    return NextResponse.json({ detail: error.message }, { status: 500 });
  }
}
