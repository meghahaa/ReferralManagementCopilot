"""Test AC-04: Node and Agent outputs are validated structured Pydantic objects."""

import pytest
from referral_copilot.models.schemas import (
    Referral,
    EligibilityResult,
    SpecialistMatch,
    SchedulingResult,
    AgentDecision,
)


def test_ac_04_pydantic_structured_models():
    decision = AgentDecision(next_agent="eligibility", action_reason="Intake complete", confidence=1.0)
    assert decision.next_agent == "eligibility"

    elig = EligibilityResult(patient_id="PAT-001", is_eligible=True, insurance_provider="Apex", policy_status="ACTIVE")
    assert elig.is_eligible is True

    match = SpecialistMatch(specialist_id="SPC-201", specialist_name="Dr. Sarah Jenkins", network_status="IN_NETWORK")
    assert match.network_status == "IN_NETWORK"

    sched = SchedulingResult(booking_id="BOOK-1234", referral_id="REF-1001", status="SCHEDULED")
    assert sched.status == "SCHEDULED"
