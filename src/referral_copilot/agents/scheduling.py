"""Scheduling Worker Agent Node.

Queries real-time specialist availability and books appointment slots,
expediting urgent referrals.
"""

import uuid
from datetime import datetime
from referral_copilot.graph.state import ReferralState
from referral_copilot.mcp.client import MCPClientAdapter


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
    avail_res = mcp_client.invoke_specialist_availability(specialist_id=spec_id)

    slots = avail_res.get("available_slots", [])

    if not slots:
        state["status"] = "UNABLE_TO_SCHEDULE"
        state["next_step"] = "reflection"
        state["logs"] = [{
            "step": "SCHEDULING_AGENT",
            "status": "NO_SLOTS",
            "timestamp": datetime.utcnow().isoformat()
        }]
        return state

    selected_slot = slots[0]
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
        "timestamp": datetime.utcnow().isoformat()
    }]
    return state
