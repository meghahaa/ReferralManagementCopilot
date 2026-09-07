"""Scheduling Worker Agent Node.

Queries real-time specialist availability and books appointment slots,
expediting urgent referrals.
"""

import uuid
from datetime import datetime, timezone
from referral_copilot.graph.state import ReferralState
from referral_copilot.mcp.client import MCPClientAdapter
from referral_copilot.models.schemas import SchedulingResult
from referral_copilot.llm.runtime import invoke_structured, live_status_log


def scheduling_agent_node(state: ReferralState) -> ReferralState:
    """Scheduling Agent Node Function.

    Args:
        state: Current ReferralState dictionary.

    Returns:
        Updated ReferralState dictionary.
    """
    spec_match = state.get("specialist_match") or {}
    spec_id = spec_match.get("specialist_id", "SPC-201")
    ref_id = state.get("referral_id", "REF-1001")
    urgency = (state.get("referral") or {}).get("urgency", "ROUTINE")

    mcp_client = MCPClientAdapter()
    try:
        avail_res = mcp_client.invoke_specialist_availability(specialist_id=spec_id)
    except Exception as exc:
        state["status"] = "TOOL_FAILURE"
        state["error_message"] = f"Availability lookup failed: {type(exc).__name__}"
        state["next_step"] = "reflection"
        state["logs"] = [{
            "step": "SCHEDULING_AGENT",
            "status": "TOOL_FAILURE",
            "tool": "specialist_availability",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }]
        return state

    slots = avail_res.get("available_slots", [])

    if not slots:
        state["status"] = "UNABLE_TO_SCHEDULE"
        state["next_step"] = "reflection"
        state["logs"] = [{
            "step": "SCHEDULING_AGENT",
            "status": "NO_SLOTS",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }]
        return state

    fallback = SchedulingResult(
        referral_id=ref_id,
        specialist_id=spec_id,
        appointment_slot=slots[0],
        status="PENDING",
    )
    selected, live, llm_error = invoke_structured(
        SchedulingResult,
        "You schedule a referral using only the supplied available slots. Select exactly one slot "
        "and never invent a time.",
        f"Referral: {ref_id}\nUrgency: {urgency}\nSpecialist: {spec_id}\nAvailable slots: {slots}",
        fallback=fallback,
    )
    selected_slot = selected.appointment_slot if selected.appointment_slot in slots else slots[0]
    booking_id = f"BOOK-{uuid.uuid4().hex[:8].upper()}"

    is_urgent = (urgency == "URGENT")
    final_status = "EXPEDITED_SCHEDULED" if is_urgent else "SCHEDULED"

    state["scheduling"] = {
        "booking_id": booking_id,
        "referral_id": ref_id,
        "specialist_id": spec_id,
        "appointment_slot": selected_slot,
        "status": final_status,
        "confirmation_notes": f"Appointment booked successfully. Priority: {urgency}."
    }

    state["status"] = final_status
    state["next_step"] = "end"

    state["logs"] = [{
        "step": "SCHEDULING_AGENT",
        "status": final_status,
        "booking_id": booking_id,
        "slot": selected_slot,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **live_status_log(live, llm_error),
    }]
    return state
