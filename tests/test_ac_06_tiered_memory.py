"""Test AC-06: Tiered Memory system (Short-term working context + Long-term fact recall)."""

import pytest
import tempfile
from pathlib import Path
from referral_copilot.memory.tiered import TieredMemoryStore


def test_ac_06_tiered_memory_write_and_recall():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_memory.db"
        memory = TieredMemoryStore(db_path=db_path)

        fact_id = memory.write_fact(
            session_id="SESS-001",
            category="PATIENT_PREFERENCE",
            key="PAT-001_preferred_clinic",
            value="Heart & Vascular Center",
            importance_score=0.9
        )

        assert fact_id.startswith("FACT-")

        recalled = memory.get_fact_by_key("PAT-001_preferred_clinic")
        assert recalled is not None
        assert recalled["value"] == "Heart & Vascular Center"
        assert recalled["importance_score"] == 0.9
