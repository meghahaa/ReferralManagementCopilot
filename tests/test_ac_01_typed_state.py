"""Test AC-01: Explicit Typed State Object shared across nodes."""

import pytest
from referral_copilot.graph.state import ReferralState


def test_ac_01_referral_state_schema():
    """Verify AC-01: ReferralState TypedDict has required attributes."""
    state: ReferralState = {
        "referral_id": "REF-1001",
        "patient_id": "PAT-001",
        "current_step": "SUPERVISOR",
        "next_step": "INTAKE",
        "status": "NEW",
        "retry_count": 0,
        "logs": [{"step": "INIT", "timestamp": "2026-09-06T16:00:00Z"}]
    }

    assert state["referral_id"] == "REF-1001"
    assert state["patient_id"] == "PAT-001"
    assert state["current_step"] == "SUPERVISOR"
    assert state["next_step"] == "INTAKE"
    assert len(state["logs"]) == 1
