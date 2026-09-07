"""Specialist Matching Worker Agent Node.

Matches appropriate in-network specialist based on clinical specialty,
location, and network tier rules.
"""

from datetime import datetime
from referral_copilot.graph.state import ReferralState
from referral_copilot.mcp.client import MCPClientAdapter


def matching_agent_node(state: ReferralState) -> ReferralState:
    """Specialist Matching Agent Node Function.

    Args:
        state: Current ReferralState dictionary.

    Returns:
        Updated ReferralState dictionary.
    """
    referral = state.get("referral") or {}
    specialty = referral.get("target_specialty", "Cardiology")

    mcp_client = MCPClientAdapter()
    network_res = mcp_client.invoke_network_lookup(specialty=specialty)

    specialists = network_res.get("specialists", [])

    if not specialists:
        # Trigger Reflection / Re-planning if no match found
        state["status"] = "UNABLE_TO_MATCH"
        state["next_step"] = "reflection"
        state["logs"] = [{
            "step": "MATCHING_AGENT",
            "status": "NO_MATCH",
            "timestamp": datetime.utcnow().isoformat()
        }]
        return state

    # Separate in-network vs out-of-network
    in_net = [s for s in specialists if s.get("network_status") == "IN_NETWORK"]
    out_net = [s for s in specialists if s.get("network_status") == "OUT_OF_NETWORK"]

    if in_net:
        best_match = in_net[0]
        state["specialist_match"] = {
            "specialist_id": best_match["specialist_id"],
            "specialist_name": best_match["name"],
            "network_status": "IN_NETWORK",
            "match_score": 0.95,
            "reasoning": f"Matched primary in-network {specialty} specialist."
        }
        state["status"] = "MATCHED"
        state["next_step"] = "scheduling"
    elif out_net:
        best_match = out_net[0]
        state["specialist_match"] = {
            "specialist_id": best_match["specialist_id"],
            "specialist_name": best_match["name"],
            "network_status": "OUT_OF_NETWORK",
            "match_score": 0.70,
            "reasoning": f"Out-of-network {specialty} specialist match requiring prior authorization."
        }
        state["status"] = "OUT_OF_NETWORK_PENDING_AUTH"
        state["next_step"] = "end"

    state["logs"] = [{
        "step": "MATCHING_AGENT",
        "status": state["status"],
        "matched_specialist_id": (state.get("specialist_match") or {}).get("specialist_id"),
        "timestamp": datetime.utcnow().isoformat()
    }]
    return state
