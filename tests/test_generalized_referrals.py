"""Regression coverage for data-driven referrals beyond the original golden set."""

from langgraph.checkpoint.memory import MemorySaver

from referral_copilot.graph.workflow import build_referral_graph


def test_urgent_out_of_network_referral_does_not_require_id_branch():
    app = build_referral_graph(checkpointer=MemorySaver())
    result = app.invoke(
        {"referral_id": "REF-1009", "retry_count": 0, "logs": []},
        config={"configurable": {"thread_id": "generalized-1009"}},
    )
    assert result["status"] == "OUT_OF_NETWORK_PENDING_AUTH"


def test_unknown_specialty_reaches_bounded_failure():
    app = build_referral_graph(checkpointer=MemorySaver())
    result = app.invoke(
        {"referral_id": "REF-1010", "retry_count": 0, "logs": []},
        config={"configurable": {"thread_id": "generalized-1010"}},
    )
    assert result["status"] == "FAILED"
    assert result["retry_count"] == 4


def test_policy_trigger_and_quarantine_are_data_driven():
    app = build_referral_graph(checkpointer=MemorySaver())
    result = app.invoke(
        {"referral_id": "REF-1011", "retry_count": 0, "logs": []},
        config={"configurable": {"thread_id": "generalized-1011"}},
    )
    assert result["status"] == "POLICY_LOOKUP_COMPLETE"
    assert result["policy_lookup_requested"] is True
    assert "<UNTRUSTED_REFERRING_PROVIDER_NOTE>" in result["quarantined_note"]
    assert result["logs"][1]["injection_flag"] is True
