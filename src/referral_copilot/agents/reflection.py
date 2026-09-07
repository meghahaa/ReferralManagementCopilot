"""Reflection / Self-Healing Agent Node.

Satisfies AC-12: Bounded reflection and self-healing loop for tool failures,
low confidence outputs, or unavailable specialist slots.
"""

import json
from datetime import datetime
from referral_copilot.config import settings
from referral_copilot.graph.state import ReferralState
from referral_copilot.models.schemas import ReflectionResult


def reflection_agent_node(state: ReferralState) -> ReferralState:
    """Reflection Node Function.

    Evaluates execution trajectory failures and determines retry / re-planning strategies.

    Args:
        state: Current ReferralState dictionary.

    Returns:
        Updated ReferralState dictionary.
    """
    retry_count = state.get("retry_count", 0) + 1
    state["retry_count"] = retry_count

    curr_status = state.get("status", "UNKNOWN")
    max_retries = settings.max_retries

    if retry_count > max_retries:
        state["reflection"] = {
            "needs_replan": False,
            "proposed_action": "TERMINATE_FAILED",
            "reflection_notes": f"Exceeded maximum reflection retry threshold ({max_retries}). Halting loop.",
            "retry_count": retry_count
        }
        state["status"] = "FAILED"
        state["next_step"] = "end"
    else:
        # Re-plan strategy based on failure status
        if curr_status == "UNABLE_TO_MATCH":
            proposed = "Expand search radius and retry matching with secondary in-network providers."
            next_agent = "matching"
        elif curr_status == "UNABLE_TO_SCHEDULE":
            proposed = "Query alternative appointment slots across partner clinics."
            next_agent = "scheduling"
        else:
            proposed = "Fallback to intake re-evaluation."
            next_agent = "intake"

        state["reflection"] = {
            "needs_replan": True,
            "proposed_action": proposed,
            "reflection_notes": f"Reflection Attempt {retry_count}: Initiating bounded self-healing recovery path.",
            "retry_count": retry_count
        }
        state["next_step"] = next_agent

    # Record Evidence Artifact for AC-12
    _record_reflection_evidence(state)

    state["logs"] = [{
        "step": "REFLECTION_AGENT",
        "status": state["status"],
        "retry_count": retry_count,
        "next_step": state["next_step"],
        "timestamp": datetime.utcnow().isoformat()
    }]
    return state


def _record_reflection_evidence(state: ReferralState) -> None:
    """Writes structured JSON reflection trace artifact for AC-12."""
    evidence_file = settings.evidence_dir / "AC-12_reflection_trace.json"
    refl_data = state.get("reflection") or {}

    log_entry = {
        "ac_id": "AC-12",
        "timestamp": datetime.utcnow().isoformat(),
        "referral_id": state.get("referral_id"),
        "status": state.get("status"),
        "retry_count": state.get("retry_count"),
        "reflection_result": refl_data,
        "next_step": state.get("next_step")
    }

    with open(evidence_file, "w") as f:
        json.dump(log_entry, f, indent=2)
