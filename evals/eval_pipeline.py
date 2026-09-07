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
            status_matched = (actual_status == expected_status)

            if status_matched:
                passed += 1
                print(f"✓ [{item['id']}] {ref_id}: Expected '{expected_status}', Actual '{actual_status}' - PASSED")
            else:
                print(f"✗ [{item['id']}] {ref_id}: Expected '{expected_status}', Actual '{actual_status}' - FAILED")

    accuracy = (passed / total) * 100 if total > 0 else 0
    print(f"\nEvaluation Summary: {passed}/{total} Passed ({accuracy:.1f}% Accuracy)")
    return accuracy


if __name__ == "__main__":
    run_evaluation()
