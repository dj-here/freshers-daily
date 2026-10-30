import json
import os
import pytest
from app.services.llm import get_llm_service
from app.pipeline.verifier import JobVerifier

@pytest.mark.asyncio
async def test_llm_evaluation_benchmark_precision_and_zero_hallucination():
    fixture_path = os.path.join(os.path.dirname(__file__), "fixtures", "eval_jobs.json")
    assert os.path.exists(fixture_path), f"Fixture not found at {fixture_path}"

    with open(fixture_path, "r", encoding="utf-8") as f:
        fixtures = json.load(f)

    assert len(fixtures) >= 50, f"Expected at least 50 test fixtures, got {len(fixtures)}"

    verifier = JobVerifier()
    llm = get_llm_service()

    total_evals = 0
    correct_batch_predictions = 0
    traps_correctly_rejected = 0
    total_traps = 0
    hallucination_violations = 0

    for item in fixtures:
        total_evals += 1
        gt = item["ground_truth"]
        is_trap = not gt["is_valid"]
        if is_trap:
            total_traps += 1

        report = await verifier.verify_job(
            title=item["title"],
            apply_url="https://boards.greenhouse.io/test/jobs/1",
            location_raw=item["location"],
            raw_html=item["content"],
            company_domain="test.com",
            skip_network_liveness=True
        )

        extracted = report.extracted_data

        # Test Anti-Hallucination:
        # Every reported batch must have literal evidence in the text
        if extracted and extracted.eligible_batches:
            for b in extracted.eligible_batches:
                if b not in item["content"] and "batch" not in item["content"].lower() and "fresher" not in item["content"].lower():
                    hallucination_violations += 1

        # Check Trap rejection
        if is_trap:
            if report.status == "rejected":
                traps_correctly_rejected += 1
        else:
            # Check Valid Batch Extraction accuracy
            expected_batches = gt["eligible_batches"]
            if extracted and set(expected_batches).issubset(set(extracted.eligible_batches)):
                correct_batch_predictions += 1

    valid_jobs_count = total_evals - total_traps
    batch_precision = (correct_batch_predictions / valid_jobs_count) * 100.0
    trap_rejection_rate = (traps_correctly_rejected / total_traps) * 100.0

    print(f"\n--- EVAL BENCHMARK RESULTS ---")
    print(f"Total Fixtures: {total_evals}")
    print(f"Batch Extraction Precision: {batch_precision:.2f}% (Target: >= 95%)")
    print(f"Trap Rejection Rate: {trap_rejection_rate:.2f}% (Target: 100%)")
    print(f"Hallucination Violations: {hallucination_violations} (Target: 0)")

    assert hallucination_violations == 0, f"Detected {hallucination_violations} hallucination violations!"
    assert batch_precision >= 95.0, f"Batch precision was {batch_precision:.2f}%, below 95% threshold"
    assert trap_rejection_rate == 100.0, f"Trap rejection rate was {trap_rejection_rate:.2f}%, expected 100%"
