"""Typed State definition for LangGraph Referral Copilot.

Satisfies AC-01: Shared TypedDict graph state object across supervisor and worker nodes.
"""

from typing import TypedDict, List, Dict, Any, Optional
from typing_extensions import Annotated
import operator


class ReferralState(TypedDict, total=False):
    """Explicit shared typed state object passed between LangGraph nodes."""

    # Primary Identifiers
    referral_id: str
    patient_id: str

    # Structured Domain Objects (as dicts or Pydantic representations)
    referral: Optional[Dict[str, Any]]
    patient: Optional[Dict[str, Any]]
    eligibility: Optional[Dict[str, Any]]
    specialist_match: Optional[Dict[str, Any]]
    scheduling: Optional[Dict[str, Any]]

    # Navigation & Execution Control
    current_step: str
    next_step: str
    status: str
    error_message: Optional[str]

    # Context Engineering & Quarantine (NFR-03)
    quarantined_note: Optional[str]
    trusted_clinical_summary: Optional[str]
    context_compressed: bool

    # Knowledge Retrieval & Reflection (AC-11, AC-12)
    rag_docs: List[Dict[str, Any]]
    memory_facts: List[Dict[str, Any]]
    policy_lookup_requested: bool
    reflection: Optional[Dict[str, Any]]
    retry_count: int

    # Trajectory Trace Log (AC-01 / NFR-04)
    logs: Annotated[List[Dict[str, Any]], operator.add]
