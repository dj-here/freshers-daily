import { NextRequest, NextResponse } from "next/server";
import { sql } from "@/lib/db";
import crypto from "crypto";

export const dynamic = "force-dynamic";

export async function POST(request: NextRequest) {
  try {
    const { email, cohort } = await request.json();
    if (!email || !cohort) {
      return NextResponse.json({ detail: "Email and cohort are required" }, { status: 400 });
    }

    const token = crypto.randomBytes(24).toString("hex");

    // Upsert subscription
    await sql`
      INSERT INTO subscriptions (email, cohort, is_active, token, created_at)
      VALUES (${email.toLowerCase()}, ${cohort}, true, ${token}, NOW())
      ON CONFLICT DO NOTHING
    `;

    return NextResponse.json({
      success: true,
      message: "Subscribed successfully! You will receive daily 06:00 IST verified digests.",
      email,
      cohort,
    });
  } catch (error: any) {
    return NextResponse.json({ detail: error.message }, { status: 500 });
  }
}
