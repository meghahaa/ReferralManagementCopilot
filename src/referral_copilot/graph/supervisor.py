"""Supervisor / Orchestrator Agent Node.

Satisfies AC-02: Supervisor orchestrator managing worker agent workflow routing.
"""

from datetime import datetime
from referral_copilot.graph.state import ReferralState
from referral_copilot.models.schemas import AgentDecision


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

    decision = AgentDecision(
        next_agent=target_agent,
        action_reason=reason,
        requires_reflection=(target_agent == "reflection"),
        confidence=1.0
    )

    state["current_step"] = "SUPERVISOR"
    state["next_step"] = decision.next_agent

    state["logs"] = [{
        "step": "SUPERVISOR",
        "decision": decision.model_dump(),
        "timestamp": datetime.utcnow().isoformat()
    }]
    return state
