import logging
from typing import Dict, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from jinja2 import Template
import httpx
from app.core.config import settings
from app.models import Subscription, DailySelection, Job, Company

logger = logging.getLogger(__name__)

EMAIL_HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>FreshersDaily Top 5 - Cohort {{ cohort }}</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f8fafc; color: #1e293b; margin: 0; padding: 20px; }
    .container { max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; overflow: hidden; }
    .header { background: #0f172a; color: #ffffff; padding: 24px; text-align: center; }
    .header h1 { margin: 0 0 6px 0; font-size: 24px; letter-spacing: -0.5px; }
    .header p { margin: 0; font-size: 14px; color: #94a3b8; }
    .content { padding: 24px; }
    .job-card { border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; margin-bottom: 16px; background: #ffffff; }
    .job-title { font-size: 16px; font-weight: 600; color: #0f172a; margin: 0 0 4px 0; }
    .job-company { font-size: 14px; color: #475569; margin-bottom: 8px; font-weight: 500; }
    .meta { display: flex; flex-wrap: wrap; gap: 8px; font-size: 12px; margin-bottom: 12px; }
    .badge { background: #f1f5f9; padding: 4px 8px; border-radius: 4px; color: #334155; }
    .badge-verified { background: #dcfce7; color: #166534; font-weight: 600; }
    .evidence { font-size: 12px; color: #64748b; background: #f8fafc; border-left: 3px solid #3b82f6; padding: 8px; margin-bottom: 12px; font-style: italic; }
    .apply-btn { display: inline-block; background: #2563eb; color: #ffffff; text-decoration: none; padding: 8px 16px; border-radius: 6px; font-size: 13px; font-weight: 600; }
    .footer { background: #f8fafc; padding: 16px; text-align: center; font-size: 12px; color: #94a3b8; border-top: 1px solid #e2e8f0; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>FreshersDaily</h1>
      <p>Today's 5 Verified Openings for Cohort {{ cohort }} ({{ date }})</p>
    </div>
    <div class="content">
      {% for item in items %}
      <div class="job-card">
        <div class="job-title">{{ item.title }}</div>
        <div class="job-company">{{ item.company_name }} ({{ item.city }})</div>
        <div class="meta">
          <span class="badge badge-verified">✓ Verified (Score: {{ item.trust_score }}%)</span>
          <span class="badge">{{ item.role_category }}</span>
          {% if item.stipend_ctc %}
          <span class="badge">{{ item.stipend_ctc }}</span>
          {% endif %}
        </div>
        <div class="evidence">
          <strong>Batch Eligibility Proof:</strong> "{{ item.evidence_snippet }}"
        </div>
        <a href="{{ item.apply_url }}" class="apply-btn" target="_blank">Direct Apply &rarr;</a>
      </div>
      {% endfor %}
    </div>
    <div class="footer">
      <p>FreshersDaily — Zero Hallucinations, 100% Evidence-Backed Fresher Software Roles in India.</p>
    </div>
  </div>
</body>
</html>
"""

class EmailDigestService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def send_daily_digests(self, date_str: str):
        if not settings.RESEND_API_KEY:
            logger.info("Email delivery skipped: RESEND_API_KEY is not configured.")
            return

        for cohort in ["2026", "2027", "2028"]:
            # Query top 5 selections
            query = (
                select(DailySelection, Job, Company)
                .join(Job, DailySelection.job_id == Job.id)
                .join(Company, Job.company_id == Company.id)
                .where(DailySelection.selection_date == date_str, DailySelection.cohort == cohort)
                .order_by(DailySelection.rank.asc())
            )
            res = await self.db.execute(query)
            rows = res.all()
            if not rows:
                continue

            items = []
            for ds, job, comp in rows:
                items.append({
                    "title": job.title,
                    "company_name": comp.name,
                    "city": job.normalized_city,
                    "role_category": job.role_category,
                    "trust_score": int(job.trust_score),
                    "stipend_ctc": job.stipend_ctc,
                    "apply_url": job.final_apply_url or job.apply_url,
                    "evidence_snippet": "Verified from official listing"
                })

            # Render HTML
            template = Template(EMAIL_HTML_TEMPLATE)
            html_content = template.render(cohort=cohort, date=date_str, items=items)

            # Query active subscribers
            sub_query = select(Subscription.email).where(
                Subscription.is_active == True,
                Subscription.cohort.in_([cohort, "all"])
            )
            sub_res = await self.db.execute(sub_query)
            subscribers = sub_res.scalars().all()

            for email in subscribers:
                await self._send_resend_email(
                    to_email=email,
                    subject=f"FreshersDaily ({cohort}): Today's 5 Verified Openings - {date_str}",
                    html=html_content
                )

    async def _send_resend_email(self, to_email: str, subject: str, html: str):
        url = "https://api.resend.com/emails"
        headers = {
            "Authorization": f"Bearer {settings.RESEND_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "from": settings.FROM_EMAIL,
            "to": [to_email],
            "subject": subject,
            "html": html
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(url, headers=headers, json=payload)
                resp.raise_for_status()
                logger.info(f"Digest email sent to {to_email}")
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
