"""Intake Worker Agent Node.

Responsible for referral intake capture, required clinical field validation,
and context quarantine of untrusted free-text referring-provider notes.
"""

import json
from datetime import datetime
from pathlib import Path
from referral_copilot.config import settings
from referral_copilot.graph.state import ReferralState
from referral_copilot.context.quarantine import sanitize_and_quarantine_note
from referral_copilot.models.schemas import Referral, Patient, ReferralStatus


def intake_agent_node(state: ReferralState) -> ReferralState:
    """Intake Agent Node Function.

    Args:
        state: Current ReferralState dictionary.

    Returns:
        Updated ReferralState dictionary.
    """
    ref_id = state.get("referral_id", "REF-1001")
    data_dir = settings.data_dir / "synthetic"

    referral_dict = state.get("referral")
    patient_dict = state.get("patient")

    # Load from synthetic files if not in state
    if not referral_dict and (data_dir / "referrals.json").exists():
        with open(data_dir / "referrals.json", "r") as f:
            for r in json.load(f):
                if r.get("referral_id") == ref_id:
                    referral_dict = r
                    break

    if referral_dict and not patient_dict and (data_dir / "patients.json").exists():
        pat_id = referral_dict.get("patient_id")
        with open(data_dir / "patients.json", "r") as f:
            for p in json.load(f):
                if p.get("patient_id") == pat_id:
                    patient_dict = p
                    break

    if not referral_dict:
        state["status"] = "FAILED"
        state["error_message"] = f"Referral ID {ref_id} not found."
        state["next_step"] = "end"
        return state

    # Context Quarantine (NFR-03)
    raw_note = referral_dict.get("untrusted_referring_provider_note", "")
    quarantined_block, injection_flag = sanitize_and_quarantine_note(raw_note)

    state["referral"] = referral_dict
    state["patient"] = patient_dict
    state["quarantined_note"] = quarantined_block

    # Required field validation
    missing_fields = []
    if not referral_dict.get("target_specialty"):
        missing_fields.append("target_specialty")
    if not referral_dict.get("icd10_code"):
        missing_fields.append("icd10_code")
    if not referral_dict.get("reason_for_referral"):
        missing_fields.append("reason_for_referral")

    if missing_fields:
        state["status"] = "INTAKE_INCOMPLETE"
        state["error_message"] = f"Missing required intake fields: {', '.join(missing_fields)}"
        state["next_step"] = "end"
    else:
        state["status"] = "INTAKE_COMPLETE"
        state["next_step"] = "eligibility"

    state["logs"] = [{
        "step": "INTAKE_AGENT",
        "status": state["status"],
        "timestamp": datetime.utcnow().isoformat(),
        "injection_flag": injection_flag
    }]
    return state
