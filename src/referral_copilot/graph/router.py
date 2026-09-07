"""Conditional Graph Router Module.

Satisfies AC-03: Defines conditional edges routing based on typed graph state.
"""

from referral_copilot.graph.state import ReferralState


def route_next(state: ReferralState) -> str:
    """Conditional Edge Routing Function.

    Evaluates referral state (urgency, eligibility, network status, completeness)
    and determines the next node in the graph workflow.

    Args:
        state: Current ReferralState dictionary.

    Returns:
        str: Target node name ('intake', 'eligibility', 'matching', 'scheduling', 'reflection', 'end')
    """
    next_step = state.get("next_step", "intake").lower()
    status = state.get("status", "")

    # Terminal states
    if next_step == "end" or status in [
        "INELIGIBLE",
        "INTAKE_INCOMPLETE",
        "NEEDS_INFO",
        "OUT_OF_NETWORK_PENDING_AUTH",
        "SCHEDULED",
        "EXPEDITED_SCHEDULED",
        "FAILED",
        "POLICY_LOOKUP_COMPLETE",
    ]:
        return "__end__"

    if next_step in ["intake", "eligibility", "matching", "scheduling", "reflection"]:
        return next_step

    return "__end__"
