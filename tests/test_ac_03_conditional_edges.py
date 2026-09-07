"""Test AC-03: Graph conditional edges route on state (out-of-network, urgent, ineligible)."""

import pytest
from referral_copilot.graph.workflow import build_referral_graph
from langgraph.checkpoint.memory import MemorySaver


def test_ac_03_conditional_routing_out_of_network():
    app = build_referral_graph(checkpointer=MemorySaver())
    state = {
        "referral_id": "REF-1002",  # Out-of-network referral scenario
        "patient_id": "PAT-002",
        "retry_count": 0,
        "logs": []
    }
    config = {"configurable": {"thread_id": "thread-ac-03-oon"}}
    res = app.invoke(state, config=config)

    assert res["status"] == "OUT_OF_NETWORK_PENDING_AUTH"


def test_ac_03_conditional_routing_ineligible():
    app = build_referral_graph(checkpointer=MemorySaver())
    state = {
        "referral_id": "REF-1004",  # Ineligible patient scenario
        "patient_id": "PAT-004",
        "retry_count": 0,
        "logs": []
    }
    config = {"configurable": {"thread_id": "thread-ac-03-inelig"}}
    res = app.invoke(state, config=config)

    assert res["status"] == "INELIGIBLE"
