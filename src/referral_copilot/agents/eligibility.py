"""Eligibility Worker Agent Node.

Checks patient insurance coverage, plan active status, and prior-authorization criteria.
"""

from datetime import datetime, timezone
from referral_copilot.graph.state import ReferralState
from referral_copilot.mcp.client import MCPClientAdapter
from referral_copilot.models.schemas import EligibilityResult
from referral_copilot.llm.runtime import invoke_structured, live_status_log


def eligibility_agent_node(state: ReferralState) -> ReferralState:
    """Eligibility Check Agent Node Function.

    Args:
        state: Current ReferralState dictionary.

    Returns:
        Updated ReferralState dictionary.
    """
    pat_id = state.get("patient_id") or (state.get("patient") or {}).get("patient_id", "PAT-001")
    mcp_client = MCPClientAdapter()

    try:
        elig_res = mcp_client.invoke_eligibility_check(patient_id=pat_id)
    except Exception as exc:
        state["status"] = "TOOL_FAILURE"
        state["error_message"] = f"Eligibility lookup failed: {type(exc).__name__}"
        state["next_step"] = "reflection"
        state["logs"] = [{
            "step": "ELIGIBILITY_AGENT",
            "status": "TOOL_FAILURE",
            "tool": "eligibility_check",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }]
        return state
    fallback = EligibilityResult(
        patient_id=pat_id,
        is_eligible=bool(elig_res.get("is_eligible")),
        insurance_provider=elig_res.get("insurance_provider", "UNKNOWN"),
        policy_status=elig_res.get("policy_status", "UNKNOWN"),
        prior_auth_required=bool(elig_res.get("prior_auth_required", False)),
        policy_notes=elig_res.get("notes", ""),
    )
    interpreted, live, llm_error = invoke_structured(
        EligibilityResult,
        "You are an eligibility reviewer. Interpret the authoritative MCP result. "
        "Never mark an inactive or missing policy eligible.",
        f"MCP eligibility result: {elig_res}",
        fallback=fallback,
    )
    # The MCP coverage result is authoritative; the model enriches the structured handoff.
    interpreted.is_eligible = bool(elig_res.get("is_eligible"))
    elig_res = interpreted.model_dump()
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
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **live_status_log(live, llm_error),
    }]
    return state
