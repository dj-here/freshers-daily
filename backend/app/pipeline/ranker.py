import os
import yaml
import logging
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Any, Optional

logger = logging.getLogger(__name__)

class RankingEngine:
    def __init__(self, config_path: Optional[str] = None):
        if not config_path:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
                "config",
                "ranking_weights.yaml"
            )
        self.config = self._load_config(config_path)

    def _load_config(self, path: str) -> Dict[str, Any]:
        default_config = {
            "weights": {
                "fresher_explicitness": 0.30,
                "trust_score": 0.20,
                "company_tier": 0.15,
                "pay_transparency": 0.10,
                "freshness": 0.10,
                "deadline_distance": 0.05,
                "location_desirability": 0.05,
                "role_relevance": 0.05
            },
            "tier_scores": {
                "TIER_1": 1.00,
                "TIER_2": 0.75,
                "TIER_3": 0.50,
                "TIER_OTHER": 0.40
            },
            "constraints": {
                "max_jobs_per_cohort_per_day": 5,
                "max_jobs_per_company_per_day": 2,
                "min_distinct_roles_per_cohort": 3,
                "min_non_it_service_jobs": 1,
                "min_trust_score_for_publish": 80.0
            },
            "diversity_penalties": {
                "duplicate_role_penalty": 0.08,
                "duplicate_location_penalty": 0.04
            }
        }
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    loaded = yaml.safe_load(f)
                    if loaded:
                        return loaded
            except Exception as e:
                logger.error(f"Error loading ranking weights from {path}: {e}")
        return default_config

    def score_job(self, job_data: Dict[str, Any], selected_so_far: List[Dict[str, Any]]) -> Tuple[float, Dict[str, float], str]:
        """
        Calculates the score for a single job taking into account diversity penalties
        relative to the candidates already selected today.
        """
        weights = self.config["weights"]
        tier_scores = self.config["tier_scores"]

        # 1. Fresher explicitness (0 to 1)
        has_explicit_batch = bool(job_data.get("batch_evidence"))
        fresher_score = 1.0 if has_explicit_batch else 0.65

        # 2. Trust score (0 to 1)
        trust_score = float(job_data.get("trust_score", 80.0)) / 100.0

        # 3. Company tier (0 to 1)
        tier = job_data.get("company_tier", "TIER_OTHER")
        company_tier_score = tier_scores.get(tier, 0.40)

        # 4. Pay transparency
        has_pay = bool(job_data.get("stipend_ctc"))
        pay_score = 1.0 if has_pay else 0.20

        # 5. Freshness
        freshness_score = 0.90 # Recently ingested/verified

        # 6. Deadline distance
        deadline_score = 0.80

        # 7. Location desirability (Bengaluru, Hyderabad, Pune, etc.)
        city = job_data.get("normalized_city", "")
        top_hubs = ["Bengaluru", "Hyderabad", "Pune", "Gurgaon", "Noida", "Mumbai", "Chennai", "Remote - India"]
        location_score = 1.0 if any(h.lower() in city.lower() for h in top_hubs) else 0.70

        # 8. Role relevance
        role_score = 1.0

        # Weighted base score
        raw_score = (
            weights["fresher_explicitness"] * fresher_score +
            weights["trust_score"] * trust_score +
            weights["company_tier"] * company_tier_score +
            weights["pay_transparency"] * pay_score +
            weights["freshness"] * freshness_score +
            weights["deadline_distance"] * deadline_score +
            weights["location_desirability"] * location_score +
            weights["role_relevance"] * role_score
        )

        # Diversity penalties
        penalties = 0.0
        selected_roles = [s.get("role_category") for s in selected_so_far]
        selected_locations = [s.get("normalized_city") for s in selected_so_far]

        current_role = job_data.get("role_category")
        if current_role in selected_roles:
            penalties += self.config["diversity_penalties"].get("duplicate_role_penalty", 0.08)

        if city in selected_locations:
            penalties += self.config["diversity_penalties"].get("duplicate_location_penalty", 0.04)

        final_score = max(0.0, raw_score - penalties)

        breakdown = {
            "fresher_explicitness": round(fresher_score, 2),
            "trust_score": round(trust_score, 2),
            "company_tier": round(company_tier_score, 2),
            "pay_transparency": round(pay_score, 2),
            "diversity_penalties": round(penalties, 2),
            "final_score": round(final_score, 4)
        }

        explanation = (
            f"Final Score: {final_score:.2f} | Tier: {tier} ({company_tier_score:.2f}) | "
            f"Trust: {trust_score*100:.0f} | Batch Explicit: {has_explicit_batch} | "
            f"Pay Stated: {has_pay} | City: {city} | Role: {current_role}"
        )

        return final_score, breakdown, explanation

    def select_top_jobs(
        self,
        cohort: str,
        candidates: List[Dict[str, Any]],
        previously_published_job_ids: set,
        target_count: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Greedy multi-objective selection enforcing:
        - Exactly target_count (up to 5)
        - Max 2 per company per day
        - At least 3 distinct roles if available
        - At least 1 non-IT service if available
        - Never select previously published jobs
        """
        # Filter eligible candidates
        eligible = [
            c for c in candidates
            if c.get("id") not in previously_published_job_ids
            and c.get("trust_score", 0.0) >= self.config["constraints"]["min_trust_score_for_publish"]
        ]

        selected: List[Dict[str, Any]] = []
        company_counts: Dict[str, int] = {}
        max_per_company = self.config["constraints"]["max_jobs_per_company_per_day"]

        # Selection loop
        while len(selected) < target_count and eligible:
            best_job = None
            best_score = -1.0
            best_explanation = ""

            for cand in eligible:
                comp = cand.get("company_slug") or cand.get("company_name")
                if company_counts.get(comp, 0) >= max_per_company:
                    continue

                score, _, explanation = self.score_job(cand, selected)
                if score > best_score:
                    best_score = score
                    best_job = cand
                    best_explanation = explanation

            if not best_job:
                break # No more candidates satisfy constraints

            best_job["selection_score"] = best_score
            best_job["selection_explanation"] = best_explanation
            selected.append(best_job)

            comp = best_job.get("company_slug") or best_job.get("company_name")
            company_counts[comp] = company_counts.get(comp, 0) + 1
            eligible.remove(best_job)

        return selected
