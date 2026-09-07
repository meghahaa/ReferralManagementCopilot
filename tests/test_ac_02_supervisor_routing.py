"""Test AC-02: Supervisor Orchestrator routing to specialized worker agents."""

import pytest
from referral_copilot.graph.workflow import build_referral_graph
from langgraph.checkpoint.memory import MemorySaver


def test_ac_02_supervisor_routing_execution():
    checkpointer = MemorySaver()
    app = build_referral_graph(checkpointer=checkpointer)

    initial_state = {
        "referral_id": "REF-1001",
        "patient_id": "PAT-001",
        "retry_count": 0,
        "logs": []
    }

    config = {"configurable": {"thread_id": "thread-ac-02-test"}}
    final_state = app.invoke(initial_state, config=config)

    assert final_state["referral_id"] == "REF-1001"
    assert final_state["status"] in ["SCHEDULED", "EXPEDITED_SCHEDULED", "ELIGIBLE", "MATCHED"]
    assert len(final_state["logs"]) >= 3
