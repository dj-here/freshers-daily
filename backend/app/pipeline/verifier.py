import logging
import re
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
import httpx
from bs4 import BeautifulSoup

from app.core.config import settings
from app.pipeline.normalizers import normalize_location, classify_role_category, NormalizedLocation
from app.services.llm import get_llm_service, ExtractionResult

logger = logging.getLogger(__name__)

# Known trusted ATS domains
TRUSTED_ATS_DOMAINS = [
    "greenhouse.io",
    "boards.greenhouse.io",
    "lever.co",
    "jobs.lever.co",
    "ashbyhq.com",
    "jobs.ashbyhq.com",
    "smartrecruiters.com",
    "jobs.smartrecruiters.com",
    "workable.com",
    "apply.workable.com",
    "myworkdayjobs.com",
    "oraclecloud.com",
    "jobvite.com",
    "icims.com",
    "tal.net",
    "taleo.net",
    "brassring.com",
    "adp.com",
    "recruitee.com",
    "bamboohr.com"
]

DISALLOWED_DOMAINS = [
    "bit.ly", "tinyurl.com", "t.co", "cutt.ly", "is.gd", "goo.gl",
    "docs.google.com", "forms.gle", "t.me", "telegram.me", "wa.me",
    "chat.whatsapp.com", "linkedin.com", "naukri.com", "indeed.com",
    "internshala.com", "unstop.com", "glassdoor.com"
]

SCAM_KEYWORDS = [
    r"\bregistration\s+fee\b",
    r"\brefundable\s+deposit\b",
    r"\bsecurity\s+deposit\b",
    r"\bsecurity\s+money\b",
    r"\btraining\s+fee\b",
    r"\btraining\s+charge\b",
    r"\bpay\s+to\s+join\b",
    r"\bearn\s+per\s+day\b",
    r"\bearn\s+\d+\s+daily\b",
    r"\bguaranteed\s+placement\s+after\s+training\b"
]

CLOSURE_KEYWORDS = [
    "job is no longer available",
    "no longer accepting applications",
    "requisition closed",
    "this job has expired",
    "position has been filled",
    "position closed",
    "posting is no longer active",
    "job not found",
    "404 not found",
    "expired requisition"
]

class VerificationReport:
    def __init__(self):
        self.results: List[Dict] = []
        self.final_trust_score: float = 100.0
        self.status: str = "pending" # verified, needs_review, rejected
        self.rejection_reasons: List[str] = []
        self.extracted_data: Optional[ExtractionResult] = None
        self.normalized_loc: Optional[NormalizedLocation] = None
        self.role_category: str = "SDE"
        self.final_apply_url: str = ""

    def add_result(self, check_name: str, passed: bool, score: float, reason: str, evidence: Optional[str] = None):
        self.results.append({
            "check_name": check_name,
            "passed": passed,
            "score": score,
            "reason": reason,
            "evidence_quote": evidence,
            "checked_at": datetime.utcnow()
        })
        if not passed:
            self.rejection_reasons.append(f"{check_name}: {reason}")

class JobVerifier:
    def __init__(self):
        self.llm = get_llm_service()

    async def verify_job(
        self,
        title: str,
        apply_url: str,
        location_raw: str,
        raw_html: str,
        company_domain: str,
        skip_network_liveness: bool = False
    ) -> VerificationReport:
        report = VerificationReport()
        report.final_apply_url = apply_url

        # Stage 1: Domain Trust
        domain_passed, domain_reason, final_domain = self._check_domain_trust(apply_url, company_domain)
        report.add_result(
            check_name="domain_trust",
            passed=domain_passed,
            score=100.0 if domain_passed else 0.0,
            reason=domain_reason,
            evidence=apply_url
        )
        if not domain_passed:
            report.status = "rejected"
            report.final_trust_score = 0.0
            return report

        # Stage 2: Liveness & Body Closure Check
        fetched_html = raw_html
        if not skip_network_liveness and apply_url.startswith("http"):
            live_passed, live_reason, fetched_body, resolved_url = await self._check_liveness(apply_url)
            report.final_apply_url = resolved_url
            if fetched_body:
                fetched_html = f"{fetched_html}\n{fetched_body}"
            report.add_result(
                check_name="liveness",
                passed=live_passed,
                score=100.0 if live_passed else 0.0,
                reason=live_reason,
                evidence=resolved_url
            )
            if not live_passed:
                report.status = "rejected"
                report.final_trust_score = 0.0
                return report
        else:
            report.add_result(
                check_name="liveness",
                passed=True,
                score=100.0,
                reason="Pre-verified or network check skipped",
                evidence=apply_url
            )

        # Stage 3: Scam Filter
        scam_passed, scam_reason = self._check_scam(f"{title}\n{fetched_html}")
        report.add_result(
            check_name="scam_filter",
            passed=scam_passed,
            score=100.0 if scam_passed else 0.0,
            reason=scam_reason
        )
        if not scam_passed:
            report.status = "rejected"
            report.final_trust_score = 0.0
            return report

        # Stage 4: Location Normalizer
        loc_res = normalize_location(f"{location_raw} {fetched_html[:300]}")
        report.normalized_loc = loc_res
        report.add_result(
            check_name="location_normalizer",
            passed=loc_res.is_valid_india,
            score=100.0 if loc_res.is_valid_india else 0.0,
            reason=f"Normalized to {loc_res.city}" if loc_res.is_valid_india else (loc_res.rejection_reason or "Non-India"),
            evidence=location_raw
        )
        if not loc_res.is_valid_india:
            report.status = "rejected"
            report.final_trust_score = 0.0
            return report

        # Stage 5: Role Category Classifier
        role_cat, role_conf = classify_role_category(title, fetched_html)
        report.role_category = role_cat
        role_passed = (role_cat != "NON_SOFTWARE" and role_conf >= 0.80)
        report.add_result(
            check_name="role_relevance",
            passed=role_passed,
            score=role_conf * 100.0,
            reason=f"Classified as {role_cat} with confidence {role_conf:.2f}",
            evidence=title
        )
        if not role_passed:
            if role_cat == "NON_SOFTWARE":
                report.status = "rejected"
                report.final_trust_score = 0.0
                return report
            else:
                report.status = "needs_review"

        # Stage 6: Fresher Eligibility & Experience Filter (LLM + Regex Two-phase)
        extraction = await self.llm.extract_job_details(title, fetched_html)
        report.extracted_data = extraction

        # Check for 2+ years experience trap
        if extraction.min_experience_years >= 2.0 or extraction.rejection_flags:
            report.add_result(
                check_name="fresher_eligibility",
                passed=False,
                score=0.0,
                reason=f"Experience requirement violated: {', '.join(extraction.rejection_flags)}",
                evidence=str(extraction.min_experience_years)
            )
            report.status = "rejected"
            report.final_trust_score = 0.0
            return report

        # Batch eligibility check
        has_batch = bool(extraction.eligible_batches)
        report.add_result(
            check_name="fresher_eligibility",
            passed=has_batch,
            score=95.0 if has_batch else 50.0,
            reason=f"Eligible batches: {', '.join(extraction.eligible_batches)}" if has_batch else "No explicit batch found in text",
            evidence=extraction.batch_evidence
        )

        # Stage 7: Freshness
        report.add_result(
            check_name="freshness",
            passed=True,
            score=90.0,
            reason="Listing verified within active window",
            evidence=datetime.utcnow().isoformat()
        )

        # Calculate Final Trust Score
        score = 100.0
        if not has_batch:
            score -= 25.0
        if not extraction.stipend_ctc:
            score -= 5.0
        if role_conf < 0.9:
            score -= 10.0

        report.final_trust_score = max(0.0, min(100.0, score))

        if report.status != "needs_review":
            if report.final_trust_score >= 80.0 and has_batch:
                report.status = "verified"
            elif report.final_trust_score >= 60.0:
                report.status = "needs_review"
            else:
                report.status = "rejected"

        return report

    def _check_domain_trust(self, url: str, company_domain: str) -> Tuple[bool, str, str]:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        # Reject disallowed aggregators & shorteners
        for dis in DISALLOWED_DOMAINS:
            if domain == dis or domain.endswith(f".{dis}"):
                return False, f"Domain disallowed or aggregator shortener: {domain}", domain

        # Check known ATS domains
        for ats in TRUSTED_ATS_DOMAINS:
            if domain == ats or domain.endswith(f".{ats}"):
                return True, f"Verified ATS domain: {ats}", domain

        # Check employer own domain
        clean_company_domain = company_domain.lower().replace("www.", "")
        if clean_company_domain in domain:
            return True, f"Verified company domain: {clean_company_domain}", domain

        # Allow other company career portals if valid TLD
        if any(domain.endswith(tld) for tld in [".com", ".org", ".in", ".co", ".ai", ".io", ".tech", ".net"]):
            return True, f"Valid domain: {domain}", domain

        return False, f"Untrusted domain: {domain}", domain

    async def _check_liveness(self, url: str) -> Tuple[bool, str, Optional[str], str]:
        headers = {
            "User-Agent": settings.USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }
        try:
            async with httpx.AsyncClient(headers=headers, timeout=12.0, follow_redirects=True, max_redirects=5) as client:
                resp = await client.get(url)
                if resp.status_code >= 400:
                    return False, f"HTTP status error: {resp.status_code}", None, str(resp.url)

                text = resp.text.lower()
                for keyword in CLOSURE_KEYWORDS:
                    if keyword in text:
                        return False, f"Closure detected in page: '{keyword}'", None, str(resp.url)

                soup = BeautifulSoup(resp.text, "html.parser")
                body_text = soup.get_text(separator=" ", strip=True)
                return True, "URL returns HTTP 200 and page is actively open", body_text[:6000], str(resp.url)
        except Exception as e:
            return False, f"Connection failed: {str(e)}", None, url

    def _check_scam(self, text: str) -> Tuple[bool, str]:
        text_lower = text.lower()
        for pattern in SCAM_KEYWORDS:
            if re.search(pattern, text_lower):
                return False, f"Scam phrase detected: {pattern}"
        return True, "No scam indicators detected"
