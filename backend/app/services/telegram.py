import logging
from typing import Dict, Any
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)

class TelegramService:
    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN

    async def broadcast_daily_summary(self, summary: Dict[str, Any]):
        if not self.bot_token:
            return

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        channel_map = {
            "2026": settings.TELEGRAM_CHANNEL_ID_2026,
            "2027": settings.TELEGRAM_CHANNEL_ID_2027,
            "2028": settings.TELEGRAM_CHANNEL_ID_2028,
        }

        selections = summary.get("selections", {})
        async with httpx.AsyncClient(timeout=10.0) as client:
            for cohort, items in selections.items():
                chat_id = channel_map.get(cohort)
                if not chat_id or not items:
                    continue

                lines = [f"🚀 *FreshersDaily — Cohort {cohort} ({summary['date']})*\n"]
                for idx, job in enumerate(items, 1):
                    lines.append(
                        f"*{idx}. {job['title']}* at {job['company_name']}\n"
                        f"📍 {job['normalized_city']} | 🏷️ {job['role_category']}\n"
                        f"🔗 [Apply Directly]({job.get('final_apply_url') or job['apply_url']})\n"
                    )

                text = "\n".join(lines)
                try:
                    await client.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"})
                except Exception as e:
                    logger.error(f"Telegram broadcast failed for cohort {cohort}: {e}")
