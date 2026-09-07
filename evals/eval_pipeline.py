"""Evaluation Pipeline for Referral Management Copilot.

Evaluates graph routing accuracy against data/golden/golden_set.jsonl benchmark.
"""

import json
from pathlib import Path
from referral_copilot.graph.workflow import build_referral_graph
from langgraph.checkpoint.memory import MemorySaver

BASE_DIR = Path(__file__).resolve().parent.parent
GOLDEN_FILE = BASE_DIR / "data" / "golden" / "golden_set.jsonl"


def run_evaluation():
    print("=== Running Referral Copilot Evaluation Pipeline ===")
    if not GOLDEN_FILE.exists():
        print(f"ERROR: Golden dataset file missing at {GOLDEN_FILE}")
        return

    app = build_referral_graph(checkpointer=MemorySaver())

    passed = 0
    total = 0

    with open(GOLDEN_FILE, "r") as f:
        for line in f:
            if not line.strip():
                continue
            item = json.loads(line)
            total += 1
            ref_id = item["referral_id"]
            expected_status = item["expected_status"]

            config = {"configurable": {"thread_id": f"eval-{ref_id}"}}
            res = app.invoke({"referral_id": ref_id, "retry_count": 0, "logs": []}, config=config)

            actual_status = res.get("status")
            actual_patient_id = (res.get("patient") or {}).get("patient_id")
            actual_eligible = (res.get("eligibility") or {}).get("is_eligible")
            if actual_eligible is None:
                actual_eligible = (res.get("patient") or {}).get("coverage_status") == "ACTIVE"
            specialist_match = res.get("specialist_match") or {}
            actual_network = specialist_match.get("network_status")
            network_check = actual_network == "IN_NETWORK" if specialist_match else None
            actual_next_step = (res.get("next_step") or "").upper()
            checks = {
                "status": actual_status == expected_status,
                "patient_id": actual_patient_id == item.get("patient_id"),
                "eligible": actual_eligible == item.get("expected_eligible"),
                "in_network": (
                    network_check == item.get("expected_in_network")
                    if specialist_match
                    else True
                ),
                "next_step": actual_next_step == item.get("expected_next_step"),
            }
            status_matched = all(checks.values())

            if status_matched:
                passed += 1
                print(f"✓ [{item['id']}] {ref_id}: {checks} - PASSED")
            else:
                print(f"✗ [{item['id']}] {ref_id}: {checks}; expected status '{expected_status}', actual '{actual_status}' - FAILED")

    accuracy = (passed / total) * 100 if total > 0 else 0
    print(f"\nEvaluation Summary: {passed}/{total} Passed ({accuracy:.1f}% Accuracy)")
    return accuracy


if __name__ == "__main__":
    run_evaluation()
