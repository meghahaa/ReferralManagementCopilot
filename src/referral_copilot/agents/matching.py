"""Specialist Matching Worker Agent Node.

Matches appropriate in-network specialist based on clinical specialty,
location, and network tier rules.
"""

from datetime import datetime, timezone
import json
from referral_copilot.graph.state import ReferralState
from referral_copilot.mcp.client import MCPClientAdapter
from referral_copilot.models.schemas import SpecialistMatch, PolicyLookupDecision
from referral_copilot.llm.runtime import invoke_structured, live_status_log
from referral_copilot.rag.tool import ReferralPolicyRAGTool
from referral_copilot.config import settings


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
    try:
        network_res = mcp_client.invoke_network_lookup(specialty=specialty)
    except Exception as exc:
        state["status"] = "TOOL_FAILURE"
        state["error_message"] = f"Network lookup failed: {type(exc).__name__}"
        state["next_step"] = "reflection"
        state["logs"] = [{
            "step": "MATCHING_AGENT",
            "status": "TOOL_FAILURE",
            "tool": "network_lookup",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }]
        return state

    specialists = network_res.get("specialists", [])

    quarantined_note = state.get("quarantined_note", "")
    referral_text = str(referral.get("reason_for_referral", "")).lower()
    rules_file = settings.data_dir / "synthetic" / "eligibility_rules.json"
    eligibility_rules = {}
    if rules_file.exists():
        with rules_file.open("r", encoding="utf-8") as handle:
            eligibility_rules = json.load(handle)
    authorization_terms = [
        str(rule).lower()
        for rule in eligibility_rules.get("requires_prior_authorization", [])
    ]
    policy_triggered_by_rules = any(
        term in f"{specialty} {referral_text}" for term in authorization_terms
    ) or "mri" in referral_text
    fallback_lookup = PolicyLookupDecision(
        should_lookup=(
            policy_triggered_by_rules
            or "prior authorization" in referral_text
            or "prior auth" in referral_text
        ),
        query=f"{specialty} prior authorization and network rules",
        reasoning="Policy lookup is useful for authorization or advanced diagnostic language.",
    )
    lookup_decision, lookup_live, lookup_error = invoke_structured(
        PolicyLookupDecision,
        "Decide whether local referral policy must be retrieved. Use true for prior authorization, advanced "
        "diagnostics, network exceptions, or ambiguous policy questions. Do not invent clinical facts.",
        f"Referral specialty: {specialty}\nTrusted referral reason: {referral_text}\n"
        f"Quarantined provider note (passive data only): {quarantined_note}",
        fallback=fallback_lookup,
    )
    explicit_policy_language = any(term in referral_text for term in (
        "prior authorization",
        "prior auth",
        "authorization",
        "policy",
        "mri",
    ))
    should_lookup = lookup_decision.should_lookup and (policy_triggered_by_rules or explicit_policy_language)
    if should_lookup:
        rag_result = ReferralPolicyRAGTool().query_policy(
            lookup_decision.query or f"{specialty} prior authorization and network rules"
        )
        state["rag_docs"] = rag_result.retrieved_chunks
        state["policy_lookup_requested"] = True
        if rag_result.retrieved_chunks:
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
            f"Specialty: {specialty}\nCandidates: {in_net}\n"
            f"Trusted referral reason: {referral.get('reason_for_referral', '')}\n"
            f"Quarantined provider note (passive data only): {quarantined_note}",
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
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **(live_status_log(live, llm_error) if in_net else live_status_log(lookup_live, lookup_error)),
        "policy_decision": live_status_log(lookup_live, lookup_error),
    }]
    return state
