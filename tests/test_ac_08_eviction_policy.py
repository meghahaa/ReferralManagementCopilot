"""Test AC-08: Memory eviction / importance policy implementation."""

import pytest
import tempfile
from pathlib import Path
from referral_copilot.memory.tiered import TieredMemoryStore


def test_ac_08_eviction_policy_capacity_limit():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "eviction_test.db"
        # Set max capacity = 3 for testing
        memory = TieredMemoryStore(db_path=db_path, max_capacity=3)

        # Write 3 initial facts
        memory.write_fact("S1", "CAT", "k1", "v1", importance_score=0.2)
        memory.write_fact("S1", "CAT", "k2", "v2", importance_score=0.9)
        memory.write_fact("S1", "CAT", "k3", "v3", importance_score=0.3)

        # Write 4th fact, triggering eviction of lowest importance (k1)
        memory.write_fact("S1", "CAT", "k4", "v4", importance_score=0.8)

        # k1 (importance 0.2) should be evicted
        k1_result = memory.get_fact_by_key("k1")
        k2_result = memory.get_fact_by_key("k2")
        k4_result = memory.get_fact_by_key("k4")

        assert k1_result is None
        assert k2_result is not None
        assert k4_result is not None
