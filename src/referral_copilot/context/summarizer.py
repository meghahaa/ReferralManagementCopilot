"""Context Compression Middleware Module.

Satisfies NFR-08: Context-window management via deterministic summarization/compression
for long referral execution trajectories.
"""

from typing import Dict, Any
from referral_copilot.graph.state import ReferralState


def compress_context(state: ReferralState, max_log_entries: int = 5) -> ReferralState:
    """Compresses large graph state trajectory logs to conserve context window tokens.

    Args:
        state: Current ReferralState graph state dictionary.
        max_log_entries: Maximum threshold for detailed step logs before compression.

    Returns:
        ReferralState: State object with compressed trajectory summary.
    """
    logs = state.get("logs", [])
    if len(logs) <= max_log_entries:
        return state

    # Deterministic compression: preserve initial step and most recent steps, compress middle
    first_step = logs[0]
    recent_steps = logs[-3:]
    compressed_middle_count = len(logs) - 4

    summary_entry = {
        "step": "CONTEXT_COMPRESSION_MIDDLEWARE",
        "action": f"Summarized {compressed_middle_count} intermediate execution steps to conserve token quota.",
        "status": "COMPRESSED",
    }

    compressed_logs = [first_step, summary_entry] + recent_steps
    state["logs"] = compressed_logs
    state["context_compressed"] = True
    return state
