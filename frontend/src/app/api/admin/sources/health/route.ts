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
    const sources = await sql`
      SELECT 
        s.id as source_id,
        s.source_type,
        s.status,
        s.last_polled_at,
        c.name as company_name
      FROM sources s
      JOIN companies c ON s.company_id = c.id
      ORDER BY s.id ASC
      LIMIT 100
    `;
    return NextResponse.json(sources);
  } catch (error: any) {
    return NextResponse.json({ detail: error.message }, { status: 500 });
  }
}
