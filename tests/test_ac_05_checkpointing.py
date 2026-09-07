"""Test AC-05: Checkpointer persists graph state (pause and resume)."""

import json
import pytest
import tempfile
from pathlib import Path
from referral_copilot.graph.workflow import build_referral_graph
from referral_copilot.graph.checkpointer import get_sqlite_checkpointer
from referral_copilot.config import settings


def test_ac_05_checkpoint_pause_and_resume():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "checkpoints.db"
        checkpointer = get_sqlite_checkpointer(db_path=db_path)
        app = build_referral_graph(checkpointer=checkpointer)

        thread_id = "thread-pause-resume-test-101"
        config = {"configurable": {"thread_id": thread_id}}

        # Phase 1: Start Referral Execution
        initial_state = {
            "referral_id": "REF-1001",
            "patient_id": "PAT-001",
            "retry_count": 0,
            "logs": []
        }

        first_run_state = app.invoke(initial_state, config=config)
        assert first_run_state["status"] in ["SCHEDULED", "EXPEDITED_SCHEDULED", "ELIGIBLE"]

        # Phase 2: Resume / Retrieve State using checkpoint thread_id
        checkpoint_tuple = app.get_state(config)
        checkpoint_state = checkpoint_tuple.values

        assert checkpoint_state["referral_id"] == "REF-1001"
        assert checkpoint_state["status"] == first_run_state["status"]

        # Generate Evidence Artifact for AC-05
        evidence_file = settings.evidence_dir / "AC-05_checkpointing.json"
        log_entry = {
            "ac_id": "AC-05",
            "thread_id": thread_id,
            "status": "PASSED",
            "checkpoint_retrieved_status": checkpoint_state["status"],
            "referral_id": checkpoint_state["referral_id"]
        }
        with open(evidence_file, "w") as f:
            json.dump(log_entry, f, indent=2)

        assert evidence_file.exists()
