"""Reflection / Self-Healing Agent Node.

Satisfies AC-12: Bounded reflection and self-healing loop for tool failures,
low confidence outputs, or unavailable specialist slots.
"""

import json
from datetime import datetime, timezone
from referral_copilot.config import settings
from referral_copilot.graph.state import ReferralState
from referral_copilot.models.schemas import ReflectionResult
from referral_copilot.llm.runtime import invoke_structured, live_status_log


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

    recovery = {
        "UNABLE_TO_MATCH": {
            "action_code": "RETRY_MATCHING",
            "next_agent": "matching",
            "proposed_action": "Expand search radius and retry matching with secondary in-network providers.",
            "failure_reason": "No suitable specialist was available for the requested referral specialty.",
        },
        "UNABLE_TO_SCHEDULE": {
            "action_code": "RETRY_SCHEDULING",
            "next_agent": "scheduling",
            "proposed_action": "Query alternative appointment slots across partner clinics.",
            "failure_reason": "The matched specialist did not return an available appointment slot.",
        },
    }.get(curr_status, {
        "action_code": "RECHECK_INTAKE",
        "next_agent": "intake",
        "proposed_action": "Re-evaluate referral intake fields before retrying the workflow.",
        "failure_reason": "The previous workflow step returned an unexpected recoverable status.",
    })

    if retry_count > max_retries:
        fallback = ReflectionResult(
            needs_replan=False,
            action_code="TERMINATE",
            trigger_status=curr_status,
            failure_reason=recovery["failure_reason"],
            proposed_action="TERMINATE_FAILED",
            reflection_notes=f"Exceeded maximum reflection retry threshold ({max_retries}). Halting loop.",
            retry_count=retry_count,
        )
        result, live, llm_error = invoke_structured(
            ReflectionResult,
            "You are a bounded referral recovery reviewer. Never exceed the retry limit and choose only "
            "matching, scheduling, intake, or termination.",
            f"Current status: {curr_status}; retry count: {retry_count}; max retries: {max_retries}",
            fallback=fallback,
        )
        state["reflection"] = result.model_dump()
        state["reflection"].update({
            "needs_replan": False,
            "action_code": "TERMINATE",
            "trigger_status": curr_status,
            "failure_reason": recovery["failure_reason"],
            "proposed_action": "TERMINATE_FAILED",
            "reflection_notes": f"Reflection terminated after exceeding the maximum retry limit ({max_retries}) for status {curr_status}.",
        })
        state["reflection"].update(live_status_log(live, llm_error))
        state["status"] = "FAILED"
        state["next_step"] = "end"
    else:
        fallback = ReflectionResult(
            needs_replan=True,
            action_code=recovery["action_code"],
            trigger_status=curr_status,
            failure_reason=recovery["failure_reason"],
            proposed_action=recovery["proposed_action"],
            reflection_notes=f"Reflection Attempt {retry_count}: Initiating bounded self-healing recovery path.",
            retry_count=retry_count,
        )
        result, live, llm_error = invoke_structured(
            ReflectionResult,
            "You are a bounded referral recovery reviewer. Recommend one safe next action based on the failure. "
            "Do not exceed the retry limit.",
            f"Current status: {curr_status}; retry count: {retry_count}; max retries: {max_retries}",
            fallback=fallback,
        )
        state["reflection"] = result.model_dump()
        state["reflection"].update({
            "needs_replan": True,
            "action_code": recovery["action_code"],
            "trigger_status": curr_status,
            "failure_reason": recovery["failure_reason"],
            "proposed_action": recovery["proposed_action"],
            "reflection_notes": f"Recovery plan for {curr_status}: retry the referral workflow through {recovery['next_agent']}.",
            "retry_count": retry_count,
        })
        state["reflection"].update(live_status_log(live, llm_error))
        state["next_step"] = recovery["next_agent"]

    # Record Evidence Artifact for AC-12
    _record_reflection_evidence(state)

    state["logs"] = [{
        "step": "REFLECTION_AGENT",
        "status": state["status"],
        "retry_count": retry_count,
        "next_step": state["next_step"],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }]
    return state


def _record_reflection_evidence(state: ReferralState) -> None:
    """Writes structured JSON reflection trace artifact for AC-12."""
    evidence_file = settings.evidence_dir / "AC-12_reflection_trace.json"
    refl_data = state.get("reflection") or {}

    log_entry = {
        "ac_id": "AC-12",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "referral_id": state.get("referral_id"),
        "status": state.get("status"),
        "retry_count": state.get("retry_count"),
        "reflection_result": refl_data,
        "next_step": state.get("next_step")
    }

    with open(evidence_file, "w") as f:
        json.dump(log_entry, f, indent=2)
