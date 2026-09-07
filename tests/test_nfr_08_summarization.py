"""Test NFR-08: Context-window summarization/compression middleware."""

import pytest
from referral_copilot.graph.state import ReferralState
from referral_copilot.context.summarizer import compress_context


def test_context_compression():
    logs = [{"step": f"STEP_{i}", "status": "OK"} for i in range(10)]
    state: ReferralState = {
        "referral_id": "REF-1001",
        "logs": logs
    }

    compressed_state = compress_context(state, max_log_entries=5)

    assert compressed_state.get("context_compressed") is True
    assert len(compressed_state["logs"]) < 10
    assert compressed_state["logs"][1]["step"] == "CONTEXT_COMPRESSION_MIDDLEWARE"
