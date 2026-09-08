"""Conditional Graph Router Module.

Satisfies AC-03: Defines conditional edges routing based on typed graph state.
"""

from referral_copilot.graph.state import ReferralState


TERMINAL_STATUSES = {
    "INELIGIBLE",
    "INTAKE_INCOMPLETE",
    "NEEDS_INFO",
    "OUT_OF_NETWORK_PENDING_AUTH",
    "SCHEDULED",
    "EXPEDITED_SCHEDULED",
    "FAILED",
    "POLICY_LOOKUP_COMPLETE",
}


def route_from_supervisor(state: ReferralState) -> str:
    """Route the supervisor decision to a worker or terminate."""
    next_step = state.get("next_step", "intake").lower()
    status = state.get("status", "")
    if next_step == "end" or status in TERMINAL_STATUSES:
        return "__end__"
    if next_step in {"intake", "eligibility", "matching", "scheduling", "reflection"}:
        return next_step
    return "__end__"


def route_after_context(state: ReferralState) -> str:
    """Return control to the supervisor after a worker/middleware cycle."""
    if state.get("status") in TERMINAL_STATUSES or state.get("next_step") == "end":
        return "__end__"
    return "supervisor"


def route_next(state: ReferralState) -> str:
    """Backward-compatible alias for supervisor routing."""
    return route_from_supervisor(state)
