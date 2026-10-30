import { NextRequest, NextResponse } from "next/server";
import { sql } from "@/lib/db";

export const dynamic = "force-dynamic";

export async function GET(
  request: NextRequest,
  { params }: { params: { cohort: string } }
) {
  let cohort = params.cohort;
  if (cohort.endsWith(".xml")) {
    cohort = cohort.replace(".xml", "");
  }

  if (!["2026", "2027", "2028"].includes(cohort)) {
    return new NextResponse("Invalid cohort", { status: 400 });
  }

  try {
    const items = await sql`
      SELECT 
        ds.rank,
        ds.selection_date,
        j.title,
        j.role_category,
        j.normalized_city,
        j.apply_url,
        j.final_apply_url,
        j.stipend_ctc,
        j.trust_score,
        c.name as company_name
      FROM daily_selections ds
      JOIN jobs j ON ds.job_id = j.id
      JOIN companies c ON j.company_id = c.id
      WHERE ds.cohort = ${cohort}
      ORDER BY ds.selection_date DESC, ds.rank ASC
      LIMIT 10
    `;

    const rssItemsXml = items
      .map(
        (i: any) => `
    <item>
      <title><![CDATA[${i.title} at ${i.company_name}]]></title>
      <link>${i.final_apply_url || i.apply_url}</link>
      <description><![CDATA[Role: ${i.role_category} | City: ${i.normalized_city} | CTC: ${i.stipend_ctc || 'Not Stated'} | Trust: ${Math.round(i.trust_score)}%]]></description>
      <guid>${i.final_apply_url || i.apply_url}</guid>
      <pubDate>${new Date().toUTCString()}</pubDate>
    </item>`
      )
      .join("");

    const xml = `<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
  <channel>
    <title>FreshersDaily - Cohort ${cohort}</title>
    <link>https://freshersdaily.in/cohort/${cohort}</link>
    <description>5 Daily Verified Fresher Software Jobs in India for Cohort ${cohort}</description>
    <language>en-in</language>
    <lastBuildDate>${new Date().toUTCString()}</lastBuildDate>
    ${rssItemsXml}
  </channel>
</rss>`;

    return new NextResponse(xml, {
      headers: {
        "Content-Type": "application/xml",
        "Cache-Control": "public, s-maxage=300, stale-while-revalidate=600",
      },
    });
  } catch (error: any) {
    return new NextResponse(error.message, { status: 500 });
  }
}
