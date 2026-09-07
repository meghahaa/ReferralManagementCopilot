"""Test AC-12: Reflection or self-healing fallback loop with evidence trace."""

import pytest
from referral_copilot.agents.reflection import reflection_agent_node
from referral_copilot.config import settings


def test_ac_12_reflection_loop_trigger():
    state = {
        "referral_id": "REF-1007",
        "status": "UNABLE_TO_MATCH",
        "retry_count": 0,
        "logs": []
    }

    updated_state = reflection_agent_node(state)

    assert updated_state["retry_count"] == 1
    assert updated_state["reflection"]["needs_replan"] is True
    assert updated_state["next_step"] == "matching"

    evidence_file = settings.evidence_dir / "AC-12_reflection_trace.json"
    assert evidence_file.exists()
