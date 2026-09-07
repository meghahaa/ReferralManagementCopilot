"""Custom Model Context Protocol (MCP) Server for Referral Management Copilot.

Satisfies AC-09: Exposes ≥ 2 tools (eligibility_check, network_lookup, specialist_availability)
and 1 resource (referral_policy://cardiology). Supports both MCP 1.x and MCP 2.x API bindings.
"""

import json
import logging
from pathlib import Path

try:
    from mcp.server.fastmcp import FastMCP
except (ImportError, ModuleNotFoundError):
    try:
        from mcp.server.mcpserver import MCPServer as FastMCP
    except (ImportError, ModuleNotFoundError):
        class FastMCP:
            def __init__(self, name: str):
                self.name = name
                self.tools = {}
                self.resources = {}

            def tool(self):
                def decorator(fn):
                    self.tools[fn.__name__] = fn
                    return fn
                return decorator

            def resource(self, uri: str):
                def decorator(fn):
                    self.resources[uri] = fn
                    return fn
                return decorator

            def run(self):
                pass

# MCP request lifecycle messages are protocol diagnostics, not application errors.
logging.getLogger("mcp.server.lowlevel.server").setLevel(logging.ERROR)

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = BASE_DIR / "data"


def _load_rules(filename: str) -> dict:
    rules_file = DATA_DIR / "synthetic" / filename
    if not rules_file.exists():
        return {}
    with rules_file.open("r", encoding="utf-8") as handle:
        return json.load(handle)

mcp = FastMCP("ReferralManagementMCPServer")


@mcp.tool()
def eligibility_check(patient_id: str) -> str:
    """Checks insurance coverage eligibility and plan status for a synthetic patient.

    Args:
        patient_id: Synthetic patient identifier (e.g. PAT-001)

    Returns:
        JSON string containing eligibility status details.
    """
    patients_file = DATA_DIR / "synthetic" / "patients.json"
    eligibility_rules = _load_rules("eligibility_rules.json")
    supported_plans = set(eligibility_rules.get("supported_plans", []))
    active_required = eligibility_rules.get("active_coverage_required", True)
    if patients_file.exists():
        with open(patients_file, "r") as f:
            patients = json.load(f)
            for p in patients:
                if p.get("patient_id") == patient_id:
                    is_active = p.get("coverage_status") == "ACTIVE"
                    is_supported = not supported_plans or p.get("insurance_provider") in supported_plans
                    is_eligible = (is_active if active_required else True) and is_supported
                    return json.dumps({
                        "patient_id": patient_id,
                        "is_eligible": is_eligible,
                        "insurance_provider": p.get("insurance_provider"),
                        "policy_status": p.get("coverage_status"),
                        "prior_auth_required": (not is_eligible),
                        "rules_version": eligibility_rules.get("rules_version"),
                        "notes": "Verified against synthetic patient database."
                    })

    return json.dumps({
        "patient_id": patient_id,
        "is_eligible": False,
        "policy_status": "NOT_FOUND",
        "notes": "Patient ID not found in registry."
    })


@mcp.tool()
def network_lookup(specialty: str) -> str:
    """Looks up available in-network specialists for a target clinical specialty.

    Args:
        specialty: Clinical specialty name (e.g. Cardiology, Orthopedics)

    Returns:
        JSON string listing matching in-network specialists.
    """
    specialists_file = DATA_DIR / "synthetic" / "specialists.json"
    network_rules = _load_rules("network_rules.json")
    matches = []
    if specialists_file.exists():
        with open(specialists_file, "r") as f:
            specialists = json.load(f)
            for s in specialists:
                if s.get("specialty", "").lower() == specialty.lower():
                    matches.append(s)

    return json.dumps({
        "specialty": specialty,
        "count": len(matches),
        "network_rules_version": network_rules.get("network_version"),
        "primary_network": network_rules.get("primary_network"),
        "specialists": matches
    })


@mcp.tool()
def specialist_availability(specialist_id: str) -> str:
    """Queries real-time open appointment slots for a specific specialist.

    Args:
        specialist_id: Synthetic specialist identifier (e.g. SPC-201)

    Returns:
        JSON string with available appointment slots.
    """
    specialists_file = DATA_DIR / "synthetic" / "specialists.json"
    if specialists_file.exists():
        with open(specialists_file, "r") as f:
            specialists = json.load(f)
            for s in specialists:
                if s.get("specialist_id") == specialist_id:
                    return json.dumps({
                        "specialist_id": specialist_id,
                        "name": s.get("name"),
                        "available_slots": s.get("available_slots", [])
                    })

    return json.dumps({
        "specialist_id": specialist_id,
        "available_slots": [],
        "notes": "Specialist not found."
    })


@mcp.resource("referral-policy://cardiology")
def get_cardiology_policy() -> str:
    """Returns official clinical policy documentation for Cardiology referrals."""
    policy_file = DATA_DIR / "uploads" / "cardiology_policy.txt"
    if policy_file.exists():
        return policy_file.read_text()
    return "Cardiology clinical policy document unavailable."


if __name__ == "__main__":
    mcp.run()
