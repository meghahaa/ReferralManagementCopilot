"""Test AC-10: Agent consumes MCP tools via adapter and generates committed evidence log."""

import pytest
from referral_copilot.mcp.client import MCPClientAdapter
from referral_copilot.config import settings


def test_ac_10_mcp_invocation_evidence():
    client = MCPClientAdapter()
    res = client.invoke_eligibility_check("PAT-001")

    assert res["is_eligible"] is True

    evidence_file = settings.evidence_dir / "AC-10_mcp_invocation.json"
    assert evidence_file.exists()
