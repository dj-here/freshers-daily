import { NextRequest, NextResponse } from "next/server";
import { sql } from "@/lib/db";

export const dynamic = "force-dynamic";

export async function POST(
  request: NextRequest,
  { params }: { params: { jobId: string } }
) {
  const adminKey = request.headers.get("x-admin-key");
  const expectedKey = process.env.ADMIN_API_KEY || "adminkey-dev-supersecret-freshersdaily-2026";
  if (adminKey !== expectedKey) {
    return NextResponse.json({ detail: "Unauthorized" }, { status: 401 });
  }

  const jobId = parseInt(params.jobId);
  const { action, reason } = await request.json();

  try {
    if (action === "approve") {
      await sql`
        UPDATE jobs
        SET status = 'verified', trust_score = GREATEST(trust_score, 85.0)
        WHERE id = ${jobId}
      `;
    } else if (action === "reject") {
      await sql`
        UPDATE jobs
        SET status = 'rejected', rejection_reason = ${reason || "Rejected by Admin"}
        WHERE id = ${jobId}
      `;
    } else {
      return NextResponse.json({ detail: "Action must be approve or reject" }, { status: 400 });
    }

    // Log admin audit
    await sql`
      INSERT INTO audit_logs (admin_user, action, target_type, target_id, details, created_at)
      VALUES ('admin', ${action + '_job'}, 'job', ${String(jobId)}, ${reason || 'None'}, NOW())
    `;

    return NextResponse.json({ success: true, jobId, action });
  } catch (error: any) {
    return NextResponse.json({ detail: error.message }, { status: 500 });
  }
}
