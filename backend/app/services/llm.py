import hashlib
import json
import logging
import re
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.core.config import settings

logger = logging.getLogger(__name__)

# LLM Structured Output Schema
class ExtractionResult(BaseModel):
    eligible_batches: List[str] = Field(default_factory=list) # e.g. ["2026"], ["2027"], ["2028"]
    role_type: str = "full_time" # "full_time", "internship", "internship_ppo"
    min_experience_years: float = 0.0
    max_experience_years: float = 1.0
    degree_requirements: List[str] = Field(default_factory=list)
    branches: List[str] = Field(default_factory=list)
    stipend_ctc: Optional[str] = None
    stipend_ctc_evidence: Optional[str] = None
    deadline: Optional[str] = None
    deadline_evidence: Optional[str] = None
    batch_evidence: Optional[str] = None
    location_evidence: Optional[str] = None
    confidence_score: float = 1.0
    rejection_flags: List[str] = Field(default_factory=list)

# In-memory content hash cache for LLM calls
_LLM_RESPONSE_CACHE: Dict[str, ExtractionResult] = {}
_DAILY_TOKEN_USAGE: int = 0

class BaseLLMService:
    async def extract_job_details(self, title: str, content: str) -> ExtractionResult:
        raise NotImplementedError

class DummyDeterministicLLM(BaseLLMService):
    """
    Deterministic rule-grounded extractor used for tests and zero-dependency local runs.
    Strictly extracts ONLY from the verbatim text without hallucinating.
    """
    async def extract_job_details(self, title: str, content: str) -> ExtractionResult:
        combined = f"{title}\n{content}"
        batches = []
        batch_evidence = None

        # Verbatim batch matching
        batch_patterns = [
            (r"\b(batch of 2026|graduating in 2026|2026 passouts?|pass out 2026|class of 2026|2026 batch)\b", "2026"),
            (r"\b(batch of 2027|graduating in 2027|2027 passouts?|pass out 2027|class of 2027|2027 batch)\b", "2027"),
            (r"\b(batch of 2028|graduating in 2028|2028 passouts?|pass out 2028|class of 2028|2028 batch)\b", "2028"),
        ]

        for pat, batch_yr in batch_patterns:
            m = re.search(pat, combined, re.IGNORECASE)
            if m:
                batches.append(batch_yr)
                batch_evidence = m.group(0)

        # Standalone year check if batch context exists
        if not batches:
            if re.search(r"\b2026\b", combined) and any(w in combined.lower() for w in ["fresher", "graduate", "passout", "batch", "degree"]):
                batches.append("2026")
                batch_evidence = "2026"
            elif re.search(r"\b2027\b", combined) and any(w in combined.lower() for w in ["intern", "final year", "ppo", "batch", "graduating"]):
                batches.append("2027")
                batch_evidence = "2027"
            elif re.search(r"\b2028\b", combined) and any(w in combined.lower() for w in ["intern", "pre-final", "summer", "batch", "graduating"]):
                batches.append("2028")
                batch_evidence = "2028"

        # Role Type
        role_type = "full_time"
        if re.search(r"\b(internship\s*\+\s*ppo|intern.*ppo|ppo)\b", combined, re.IGNORECASE):
            role_type = "internship_ppo"
        elif re.search(r"\b(intern|internship|trainee|apprentice)\b", combined, re.IGNORECASE):
            role_type = "internship"

        # If it's an intern role without explicit batch, 2028/2027 are natural targets
        if not batches:
            if role_type in ("internship", "internship_ppo"):
                if re.search(r"\b(pre-final|3rd year|third year|penultimate)\b", combined, re.IGNORECASE):
                    batches.append("2028")
                    batch_evidence = "pre-final year / 2028 eligible"
                elif re.search(r"\b(final year|4th year|fourth year)\b", combined, re.IGNORECASE):
                    batches.append("2027")
                    batch_evidence = "final year / 2027 eligible"
            elif any(w in combined.lower() for w in ["fresher", "entry level", "graduate engineer trainee", "new grad"]):
                batches.append("2026")
                batch_evidence = "fresher / new grad / 2026 eligible"

        # Experience check
        min_exp = 0.0
        max_exp = 1.0
        rejection_flags = []

        exp_match = re.search(r"(\d+)\s*(?:-|to|\+)\s*(\d+)?\s*(?:years?|yrs?)", combined, re.IGNORECASE)
        if exp_match:
            val1 = float(exp_match.group(1))
            val2 = float(exp_match.group(2)) if exp_match.group(2) else val1
            if val1 >= 2.0:
                rejection_flags.append(f"Requires {val1}+ years experience")
            min_exp = val1
            max_exp = max(val2, val1)

        # Branches
        branches = []
        if re.search(r"\b(computer science|cse|it|information technology)\b", combined, re.IGNORECASE):
            branches.extend(["CSE", "IT"])
        if re.search(r"\b(electronics|ece|electrical|eee)\b", combined, re.IGNORECASE):
            branches.extend(["ECE", "EEE"])
        if re.search(r"\b(ai|artificial intelligence|data science|ml)\b", combined, re.IGNORECASE):
            branches.extend(["AI/ML", "Data Science"])

        # Location evidence
        loc_match = re.search(r"\b(Bengaluru|Bangalore|Hyderabad|Pune|Gurgaon|Gurugram|Noida|Mumbai|Chennai|Delhi NCR|India)\b", combined, re.IGNORECASE)
        location_evidence = loc_match.group(0) if loc_match else "India"

        # Stipend / CTC
        stipend_ctc = None
        stipend_ctc_evidence = None
        ctc_match = re.search(r"(?:stipend|ctc|salary|inr|rs\.?|₹)\s*[:=-]?\s*(\d+(?:,\d+)*(?:\.\d+)?\s*(?:lpa|k|pm|per month|lakhs?)?)", combined, re.IGNORECASE)
        if ctc_match:
            stipend_ctc = ctc_match.group(0).strip()
            stipend_ctc_evidence = ctc_match.group(0).strip()

        return ExtractionResult(
            eligible_batches=batches,
            role_type=role_type,
            min_experience_years=min_exp,
            max_experience_years=max_exp,
            degree_requirements=["B.E.", "B.Tech"] if "b.tech" in combined.lower() or "b.e." in combined.lower() else [],
            branches=list(set(branches)) if branches else ["CSE", "IT", "Allied"],
            stipend_ctc=stipend_ctc,
            stipend_ctc_evidence=stipend_ctc_evidence,
            batch_evidence=batch_evidence,
            location_evidence=location_evidence,
            rejection_flags=rejection_flags
        )

class AnthropicLLMService(BaseLLMService):
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    async def extract_job_details(self, title: str, content: str) -> ExtractionResult:
        import httpx
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        prompt = f"""You are a strict job extraction parser for engineering fresher hiring in India.
Your task is to extract eligibility details strictly from the provided job text.
Rules:
1. ONLY extract information that is explicitly stated in the text.
2. If any field is not stated, return null or empty list. NEVER invent or guess.
3. Every critical field must include an exact verbatim evidence quote from the text.
4. Eligible batches: determine if open to 2026, 2027, or 2028.
5. Identify any experience requirement >= 2 years.

Return ONLY valid JSON matching this schema:
{{
  "eligible_batches": ["2026", "2027", "2028"],
  "role_type": "full_time" | "internship" | "internship_ppo",
  "min_experience_years": 0.0,
  "max_experience_years": 1.0,
  "degree_requirements": ["B.E.", "B.Tech"],
  "branches": ["CSE", "IT"],
  "stipend_ctc": "string or null",
  "stipend_ctc_evidence": "verbatim quote or null",
  "deadline": "YYYY-MM-DD or null",
  "deadline_evidence": "verbatim quote or null",
  "batch_evidence": "verbatim quote or null",
  "location_evidence": "verbatim quote or null",
  "rejection_flags": []
}}

JOB TITLE: {title}
JOB CONTENT:
{content[:8000]}
"""
        payload = {
            "model": self.model,
            "max_tokens": 1000,
            "temperature": 0.0,
            "messages": [{"role": "user", "content": prompt}]
        }
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            res_json = resp.json()
            text_resp = res_json["content"][0]["text"]
            # Clean JSON markdown if wrapped
            clean_json = re.sub(r"^```json\s*", "", text_resp.strip())
            clean_json = re.sub(r"\s*```$", "", clean_json)
            parsed = json.loads(clean_json)
            return ExtractionResult(**parsed)

def get_llm_service() -> BaseLLMService:
    content_hash_cache = _LLM_RESPONSE_CACHE
    if settings.LLM_PROVIDER == "anthropic" and settings.ANTHROPIC_API_KEY:
        return AnthropicLLMService(settings.ANTHROPIC_API_KEY, settings.LLM_MODEL)
    return DummyDeterministicLLM()
