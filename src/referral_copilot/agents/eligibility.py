"""Eligibility Worker Agent Node.

Checks patient insurance coverage, plan active status, and prior-authorization criteria.
"""

from datetime import datetime
from referral_copilot.graph.state import ReferralState
from referral_copilot.mcp.client import MCPClientAdapter


def eligibility_agent_node(state: ReferralState) -> ReferralState:
    """Eligibility Check Agent Node Function.

    Args:
        state: Current ReferralState dictionary.

    Returns:
        Updated ReferralState dictionary.
    """
    pat_id = state.get("patient_id") or (state.get("patient") or {}).get("patient_id", "PAT-001")
    mcp_client = MCPClientAdapter()

    elig_res = mcp_client.invoke_eligibility_check(patient_id=pat_id)
    state["eligibility"] = elig_res

    if elig_res.get("is_eligible"):
        state["status"] = "ELIGIBLE"
        state["next_step"] = "matching"
    else:
        state["status"] = "INELIGIBLE"
        state["next_step"] = "end"

    state["logs"] = [{
        "step": "ELIGIBILITY_AGENT",
        "status": state["status"],
        "is_eligible": elig_res.get("is_eligible"),
        "timestamp": datetime.utcnow().isoformat()
    }]
    return state
