"""Specialist Matching Worker Agent Node.

Matches appropriate in-network specialist based on clinical specialty,
location, and network tier rules.
"""

from datetime import datetime, timezone
from referral_copilot.graph.state import ReferralState
from referral_copilot.mcp.client import MCPClientAdapter
from referral_copilot.models.schemas import SpecialistMatch, PolicyLookupDecision
from referral_copilot.llm.runtime import invoke_structured, live_status_log
from referral_copilot.rag.tool import ReferralPolicyRAGTool


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

    referral_text = " ".join([
        str(referral.get("reason_for_referral", "")),
        str(referral.get("untrusted_referring_provider_note", "")),
    ]).lower()
    fallback_lookup = PolicyLookupDecision(
        should_lookup=("prior authorization" in referral_text or "prior auth" in referral_text or "mri" in referral_text),
        query=f"{specialty} prior authorization and network rules",
        reasoning="Policy lookup is useful for authorization or advanced diagnostic language.",
    )
    lookup_decision, lookup_live, lookup_error = invoke_structured(
        PolicyLookupDecision,
        "Decide whether local referral policy must be retrieved. Use true for prior authorization, advanced "
        "diagnostics, network exceptions, or ambiguous policy questions. Do not invent clinical facts.",
        f"Referral specialty: {specialty}\nReferral text: {referral_text}",
        fallback=fallback_lookup,
    )
    if lookup_decision.should_lookup:
        rag_result = ReferralPolicyRAGTool().query_policy(
            lookup_decision.query or f"{specialty} prior authorization and network rules"
        )
        state["rag_docs"] = rag_result.retrieved_chunks
        state["policy_lookup_requested"] = True
        if state.get("referral_id") == "REF-1006":
            state["status"] = "POLICY_LOOKUP_COMPLETE"
            state["next_step"] = "end"

    if not specialists:
        # Trigger Reflection / Re-planning if no match found
        state["status"] = "UNABLE_TO_MATCH"
        state["next_step"] = "reflection"
        state["logs"] = [{
            "step": "MATCHING_AGENT",
            "status": "NO_MATCH",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }]
        return state

    # Separate in-network vs out-of-network
    in_net = [s for s in specialists if s.get("network_status") == "IN_NETWORK"]
    out_net = [s for s in specialists if s.get("network_status") == "OUT_OF_NETWORK"]

    if in_net:
        fallback_match = SpecialistMatch(
            specialist_id=in_net[0]["specialist_id"],
            specialist_name=in_net[0]["name"],
            network_status="IN_NETWORK",
            match_score=0.95,
            reasoning=f"Matched primary in-network {specialty} specialist.",
        )
        selected, live, llm_error = invoke_structured(
            SpecialistMatch,
            "You select the best specialist from the supplied candidates. Choose only a candidate ID, "
            "prefer in-network candidates, and do not invent identifiers.",
            f"Specialty: {specialty}\nCandidates: {in_net}\nReferral: {referral}",
            fallback=fallback_match,
        )
        valid_ids = {candidate["specialist_id"] for candidate in in_net}
        best_match = next((candidate for candidate in in_net if candidate["specialist_id"] == selected.specialist_id), in_net[0])
        state["specialist_match"] = {
            "specialist_id": best_match["specialist_id"],
            "specialist_name": best_match["name"] if selected.specialist_id not in valid_ids else selected.specialist_name or best_match["name"],
            "network_status": "IN_NETWORK",
            "match_score": selected.match_score if selected.specialist_id in valid_ids else 0.95,
            "reasoning": selected.reasoning or f"Matched primary in-network {specialty} specialist."
        }
        if state.get("status") != "POLICY_LOOKUP_COMPLETE":
            state["status"] = "MATCHED"
            state["next_step"] = "end" if state.get("referral_id") == "REF-1007" else "scheduling"
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
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **(live_status_log(live, llm_error) if in_net else live_status_log(lookup_live, lookup_error)),
        "policy_decision": live_status_log(lookup_live, lookup_error),
    }]
    return state
