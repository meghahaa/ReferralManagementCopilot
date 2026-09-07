"""Single-Command Pipeline Runner for Referral Management Copilot.

Executes the complete end-to-end pipeline in sequence:
1. Validate Synthetic Datasets
2. Index Clinical Policy RAG Documents
3. Run Golden Benchmark Evaluation Pipeline
4. Execute Pytest Test Suite
5. Generate Evidence JSON Artifacts
6. Execute End-to-End Referral Workflow Demo
"""

import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def run_step(step_name: str, command: list):
    print(f"\n==========================================================================")
    print(f"▶ STEP: {step_name}")
    print(f"==========================================================================")
    result = subprocess.run(command, cwd=BASE_DIR)
    if result.returncode != 0:
        print(f"\n❌ STEP FAILED: {step_name} (Exit Code: {result.returncode})")
        sys.exit(result.returncode)
    print(f"✓ {step_name} COMPLETED SUCCESSFULLY.")


def main():
    print("🚀 Starting Complete Referral Management Copilot Pipeline...")

    python_executable = sys.executable

    # 1. Seed & Validate Data
    run_step(
        "1. Validate Synthetic Datasets",
        [python_executable, "scripts/seed_data.py"]
    )

    # 2. Index RAG Policy Documents
    run_step(
        "2. Index Clinical Policy RAG Documents",
        [python_executable, "scripts/index_rag.py"]
    )

    # 3. Run Benchmark Evaluation Pipeline
    run_step(
        "3. Run Golden Benchmark Evaluation Pipeline",
        [python_executable, "evals/eval_pipeline.py"]
    )

    # 4. Execute Pytest Suite
    run_step(
        "4. Run Automated Pytest Test Suite",
        [python_executable, "-m", "pytest", "tests/", "-v"]
    )

    # 5. Generate Evidence JSON Artifacts
    run_step(
        "5. Generate Evidence JSON Artifacts",
        [python_executable, "scripts/generate_evidence.py"]
    )

    # 6. Execute Referral Workflow Demo
    run_step(
        "6. Run End-to-End Referral Demo (REF-1001)",
        [python_executable, "scripts/run_demo.py", "REF-1001"]
    )

    print("\n==========================================================================")
    print("🎉 FULL PIPELINE EXECUTED SUCCESSFULLY WITH ZERO ERRORS!")
    print("==========================================================================\n")


if __name__ == "__main__":
    main()
