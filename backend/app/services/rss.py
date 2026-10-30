from datetime import datetime
from typing import List, Dict, Any
from xml.sax.saxutils import escape

def generate_cohort_rss_feed(cohort: str, date_str: str, items: List[Dict[str, Any]]) -> str:
    rss_items = []
    for item in items:
        title = escape(f"{item.get('title')} at {item.get('company_name')}")
        link = escape(item.get("final_apply_url") or item.get("apply_url", ""))
        desc = escape(
            f"Role: {item.get('role_category')} | City: {item.get('normalized_city')} | "
            f"Stipend/CTC: {item.get('stipend_ctc', 'Not Stated')} | Trust Score: {item.get('trust_score', 80)}%"
        )
        rss_items.append(f"""
    <item>
      <title>{title}</title>
      <link>{link}</link>
      <description>{desc}</description>
      <guid>{link}</guid>
      <pubDate>{datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}</pubDate>
    </item>""")

    feed_xml = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
  <channel>
    <title>FreshersDaily - Cohort {cohort}</title>
    <link>https://freshersdaily.in/cohort/{cohort}</link>
    <description>5 Daily Verified Fresher Software Jobs in India for Cohort {cohort}</description>
    <language>en-in</language>
    <lastBuildDate>{datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}</lastBuildDate>
    {''.join(rss_items)}
  </channel>
</rss>"""
    return feed_xml
