"""Pydantic Domain Models and Handoff Schemas for Referral Management Copilot."""

from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class UrgencyLevel(str, Enum):
    ROUTINE = "ROUTINE"
    URGENT = "URGENT"
    EMERGENCY = "EMERGENCY"


class NetworkStatus(str, Enum):
    IN_NETWORK = "IN_NETWORK"
    OUT_OF_NETWORK = "OUT_OF_NETWORK"
    UNKNOWN = "UNKNOWN"


class ReferralStatus(str, Enum):
    NEW = "NEW"
    INTAKE_COMPLETE = "INTAKE_COMPLETE"
    INTAKE_INCOMPLETE = "INTAKE_INCOMPLETE"
    NEEDS_INFO = "NEEDS_INFO"
    ELIGIBLE = "ELIGIBLE"
    INELIGIBLE = "INELIGIBLE"
    MATCHED = "MATCHED"
    UNABLE_TO_MATCH = "UNABLE_TO_MATCH"
    SCHEDULED = "SCHEDULED"
    EXPEDITED_SCHEDULED = "EXPEDITED_SCHEDULED"
    OUT_OF_NETWORK_PENDING_AUTH = "OUT_OF_NETWORK_PENDING_AUTH"
    POLICY_LOOKUP_COMPLETE = "POLICY_LOOKUP_COMPLETE"
    FAILED = "FAILED"


class Referral(BaseModel):
    """Synthetic patient referral object."""
    referral_id: str = Field(..., description="Unique referral identifier (e.g. REF-1001)")
    patient_id: str = Field(..., description="Synthetic patient identifier (e.g. PAT-001)")
    referring_provider_id: str = Field(..., description="Synthetic provider identifier")
    target_specialty: str = Field(..., description="Target clinical specialty (e.g. Cardiology)")
    urgency: UrgencyLevel = Field(default=UrgencyLevel.ROUTINE)
    icd10_code: Optional[str] = Field(default=None, description="Primary ICD-10 diagnosis code")
    reason_for_referral: Optional[str] = Field(default=None, description="Clinical reason for referral")
    untrusted_referring_provider_note: Optional[str] = Field(
        default=None,
        description="Quarantined free-text note from referring provider"
    )
    status: ReferralStatus = Field(default=ReferralStatus.NEW)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class Patient(BaseModel):
    """Synthetic patient demographic and coverage record."""
    patient_id: str
    name: str
    dob: str
    gender: str
    insurance_provider: str
    policy_number: str
    coverage_status: str
    effective_date: str
    expiration_date: str
    preferred_language: str = "English"
    zip_code: str = "90210"


class ReferringProvider(BaseModel):
    """Synthetic referring provider record."""
    provider_id: str
    name: str
    npi: str
    specialty: str
    clinic_name: str
    phone: str
    network_affinity: str


class Specialist(BaseModel):
    """Synthetic specialist physician record."""
    specialist_id: str
    name: str
    npi: str
    specialty: str
    sub_specialty: str
    network_status: NetworkStatus
    accepted_insurances: List[str]
    clinic_location: str
    zip_code: str
    rating: float = 4.5
    available_slots: List[str] = Field(default_factory=list)


class EligibilityResult(BaseModel):
    """Structured result from Eligibility Check Agent / Tool."""
    patient_id: str
    is_eligible: bool
    insurance_provider: str
    policy_status: str
    prior_auth_required: bool = False
    policy_notes: str = ""


class SpecialistMatch(BaseModel):
    """Structured result from Specialist Matching Agent / Tool."""
    specialist_id: Optional[str] = None
    specialist_name: Optional[str] = None
    network_status: NetworkStatus = NetworkStatus.UNKNOWN
    match_score: float = 0.0
    location_zip: Optional[str] = None
    reasoning: str = ""


class SchedulingResult(BaseModel):
    """Structured result from Scheduling Agent / Tool."""
    booking_id: Optional[str] = None
    referral_id: str
    specialist_id: Optional[str] = None
    appointment_slot: Optional[str] = None
    status: str = "PENDING"
    confirmation_notes: str = ""


class AgentDecision(BaseModel):
    """Structured output from Supervisor Router agent."""
    next_agent: str = Field(
        ...,
        description="Target worker node name (intake, eligibility, matching, scheduling, reflection, end)"
    )
    action_reason: str = Field(..., description="Explanation for routing decision")
    requires_reflection: bool = Field(default=False)
    confidence: float = Field(default=1.0)


class PolicyLookupDecision(BaseModel):
    """Structured decision for on-demand referral-policy retrieval."""
    should_lookup: bool
    query: str
    reasoning: str = ""


class ReflectionResult(BaseModel):
    """Structured result from Reflection / Self-Healing Agent."""
    needs_replan: bool
    proposed_action: str
    reflection_notes: str
    retry_count: int = 0


class RAGQueryResult(BaseModel):
    """Result of an Agentic-RAG policy lookup."""
    query: str
    retrieved_chunks: List[Dict[str, Any]]
    relevance_score: float
    policy_source: str


class MCPToolCallRecord(BaseModel):
    """Evidence record for an MCP Tool invocation."""
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    tool_name: str
    input_params: Dict[str, Any]
    output_data: Any
    ac_id: str = "AC-10"
