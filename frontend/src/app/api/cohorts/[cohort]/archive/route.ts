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

  try {
    const dates = await sql`
      SELECT DISTINCT selection_date
      FROM daily_selections
      WHERE cohort = ${cohort}
      ORDER BY selection_date DESC
    `;
    const archiveDates = dates.map((d: any) => d.selection_date);
    return NextResponse.json({ cohort, archive_dates: archiveDates });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
