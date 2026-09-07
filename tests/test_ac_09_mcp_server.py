"""Test AC-09: Custom MCP Server (>=2 tools and 1 resource)."""

import json
import pytest
from referral_copilot.mcp.server import (
    eligibility_check,
    network_lookup,
    specialist_availability,
    get_cardiology_policy,
)


def test_ac_09_mcp_tools_and_resource():
    # Tool 1: eligibility_check
    elig_res = json.loads(eligibility_check("PAT-001"))
    assert elig_res["patient_id"] == "PAT-001"
    assert elig_res["is_eligible"] is True

    # Tool 2: network_lookup
    net_res = json.loads(network_lookup("Cardiology"))
    assert net_res["specialty"] == "Cardiology"
    assert net_res["count"] >= 1

    # Tool 3: specialist_availability
    avail_res = json.loads(specialist_availability("SPC-201"))
    assert avail_res["specialist_id"] == "SPC-201"
    assert len(avail_res["available_slots"]) > 0

    # Resource 1: referral_policy
    policy_text = get_cardiology_policy()
    assert "CLINICAL POLICY DIRECTIVE" in policy_text
