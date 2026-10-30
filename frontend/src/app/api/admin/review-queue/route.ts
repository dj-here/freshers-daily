import { NextRequest, NextResponse } from "next/server";
import { sql } from "@/lib/db";

export const dynamic = "force-dynamic";

export async function GET(request: NextRequest) {
  const adminKey = request.headers.get("x-admin-key");
  const expectedKey = process.env.ADMIN_API_KEY || "adminkey-dev-supersecret-freshersdaily-2026";
  if (adminKey !== expectedKey) {
    return NextResponse.json({ detail: "Unauthorized" }, { status: 401 });
  }

  try {
    const jobs = await sql`
      SELECT 
        j.id,
        j.title,
        j.role_category,
        j.normalized_city,
        j.apply_url,
        j.final_apply_url,
        j.trust_score,
        j.status,
        j.rejection_reason,
        c.name as company_name,
        c.slug as company_slug,
        c.tier as company_tier
      FROM jobs j
      JOIN companies c ON j.company_id = c.id
      WHERE j.status = 'needs_review'
      ORDER BY j.created_at DESC
    `;
    return NextResponse.json(jobs);
  } catch (error: any) {
    return NextResponse.json({ detail: error.message }, { status: 500 });
  }
}
