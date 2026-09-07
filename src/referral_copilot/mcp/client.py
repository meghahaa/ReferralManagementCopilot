"""MCP Client Adapter for Referral Copilot.

Satisfies AC-10: Consumes MCP tools/resources and logs structured execution transcripts.
"""

import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from referral_copilot.config import settings
from referral_copilot.models.schemas import MCPToolCallRecord
from referral_copilot.mcp.server import (
    eligibility_check,
    network_lookup,
    specialist_availability,
    get_cardiology_policy,
)


class MCPClientAdapter:
    """Adapter for invoking custom MCP tools and recording evidence transcripts."""

    def __init__(self):
        self.evidence_dir = settings.evidence_dir

    def invoke_eligibility_check(self, patient_id: str) -> Dict[str, Any]:
        """Invokes MCP tool `eligibility_check`."""
        raw_res = eligibility_check(patient_id=patient_id)
        res_data = json.loads(raw_res)

        record = MCPToolCallRecord(
            timestamp=datetime.utcnow().isoformat(),
            tool_name="eligibility_check",
            input_params={"patient_id": patient_id},
            output_data=res_data,
            ac_id="AC-10"
        )
        self._record_evidence("AC-10_mcp_invocation.json", record)
        return res_data

    def invoke_network_lookup(self, specialty: str) -> Dict[str, Any]:
        """Invokes MCP tool `network_lookup`."""
        raw_res = network_lookup(specialty=specialty)
        res_data = json.loads(raw_res)

        record = MCPToolCallRecord(
            timestamp=datetime.utcnow().isoformat(),
            tool_name="network_lookup",
            input_params={"specialty": specialty},
            output_data=res_data,
            ac_id="AC-10"
        )
        self._record_evidence("AC-10_mcp_invocation.json", record)
        return res_data

    def invoke_specialist_availability(self, specialist_id: str) -> Dict[str, Any]:
        """Invokes MCP tool `specialist_availability`."""
        raw_res = specialist_availability(specialist_id=specialist_id)
        res_data = json.loads(raw_res)

        record = MCPToolCallRecord(
            timestamp=datetime.utcnow().isoformat(),
            tool_name="specialist_availability",
            input_params={"specialist_id": specialist_id},
            output_data=res_data,
            ac_id="AC-10"
        )
        self._record_evidence("AC-10_mcp_invocation.json", record)
        return res_data

    def read_cardiology_policy_resource(self) -> str:
        """Invokes MCP resource `referral_policy://cardiology`."""
        return get_cardiology_policy()

    def _record_evidence(self, filename: str, record: MCPToolCallRecord) -> None:
        """Appends tool invocation record to evidence JSON log."""
        evidence_file = self.evidence_dir / filename
        logs = []
        if evidence_file.exists():
            try:
                with open(evidence_file, "r") as f:
                    logs = json.load(f)
                    if not isinstance(logs, list):
                        logs = [logs]
            except Exception:
                logs = []

        logs.append(record.model_dump())
        with open(evidence_file, "w") as f:
            json.dump(logs, f, indent=2)
