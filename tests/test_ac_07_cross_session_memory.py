"""Test AC-07: Cross-Session Memory Persistence Test and Log Generation."""

import json
import pytest
import tempfile
from datetime import datetime
from pathlib import Path
from referral_copilot.memory.tiered import TieredMemoryStore
from referral_copilot.config import settings


def test_ac_07_cross_session_memory_persistence():
    """Verify AC-07: Fact stored in Session A is recalled in a newly instantiated Session B."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "cross_session_memory.db"

        # 1. Session A: Store Synthetic Fact
        session_a_id = "SESSION-ALPHA-101"
        memory_store_a = TieredMemoryStore(db_path=db_path)
        fact_id = memory_store_a.write_fact(
            session_id=session_a_id,
            category="PATIENT_CLINICAL_PREFERENCE",
            key="PAT-003_contrast_allergy",
            value="Severe reaction to iodine contrast agents",
            referral_id="REF-1003",
            importance_score=0.95
        )
        assert fact_id is not None

        # Terminate Session A reference
        del memory_store_a

        # 2. Session B: Start brand new session instance, read from disk
        session_b_id = "SESSION-BETA-202"
        memory_store_b = TieredMemoryStore(db_path=db_path)

        recalled_fact = memory_store_b.get_fact_by_key("PAT-003_contrast_allergy")

        # 3. Verify cross-session recall
        assert recalled_fact is not None
        assert recalled_fact["session_id"] == session_a_id
        assert recalled_fact["value"] == "Severe reaction to iodine contrast agents"
        assert recalled_fact["importance_score"] == 0.95

        # 4. Generate structured evidence log artifact for repo commit
        evidence_log = {
            "ac_id": "AC-07",
            "timestamp": datetime.utcnow().isoformat(),
            "test_status": "PASSED",
            "session_a": {
                "session_id": session_a_id,
                "fact_stored": "PAT-003_contrast_allergy",
                "value": "Severe reaction to iodine contrast agents"
            },
            "session_b": {
                "session_id": session_b_id,
                "recalled_fact": recalled_fact
            }
        }

        evidence_file = settings.evidence_dir / "AC-07_cross_session_memory.json"
        with open(evidence_file, "w") as f:
            json.dump(evidence_log, f, indent=2)

        assert evidence_file.exists()
