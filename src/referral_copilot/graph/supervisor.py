"""Supervisor / Orchestrator Agent Node.

Satisfies AC-02: Supervisor orchestrator managing worker agent workflow routing.
"""

from datetime import datetime, timezone
from referral_copilot.graph.state import ReferralState
from referral_copilot.models.schemas import AgentDecision
from referral_copilot.llm.runtime import invoke_structured, live_status_log


def supervisor_agent_node(state: ReferralState) -> ReferralState:
    """Supervisor Agent Node Function.

    Args:
        state: Current ReferralState dictionary.

    Returns:
        Updated ReferralState dictionary.
    """
    status = state.get("status", "NEW")
    current_next = state.get("next_step")
    # Initial routing logic
    if not current_next or status == "NEW":
        target_agent = "intake"
        reason = "New referral submitted; routing to Intake Agent for field validation."
    else:
        target_agent = current_next
        reason = f"Routing to {target_agent} agent based on current status '{status}'."

    fallback = AgentDecision(
        next_agent=target_agent,
        action_reason=reason,
        requires_reflection=(target_agent == "reflection"),
        confidence=1.0
    )
    decision, live, llm_error = invoke_structured(
        AgentDecision,
        "You are the referral workflow supervisor. Select only one next agent from intake, eligibility, "
        "matching, scheduling, reflection, or end. Respect terminal statuses and never skip eligibility.",
        f"Current status: {status}; proposed next step: {target_agent}; referral state keys: {list(state.keys())}",
        fallback=fallback,
    )
    allowed = {"intake", "eligibility", "matching", "scheduling", "reflection", "end"}
    if decision.next_agent.lower() not in allowed:
        decision = fallback
    if status in {"INELIGIBLE", "INTAKE_INCOMPLETE", "NEEDS_INFO", "OUT_OF_NETWORK_PENDING_AUTH", "SCHEDULED", "EXPEDITED_SCHEDULED", "FAILED", "POLICY_LOOKUP_COMPLETE"}:
        decision = fallback

    state["current_step"] = "SUPERVISOR"
    state["next_step"] = decision.next_agent

    state["logs"] = [{
        "step": "SUPERVISOR",
        "decision": decision.model_dump(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **live_status_log(live, llm_error),
    }]
    return state
