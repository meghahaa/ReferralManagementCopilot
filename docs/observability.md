# Observability & Structured Tracing Architecture

This document defines logging, structured tracing, and trajectory recording across the Referral Management Copilot.

---

## 1. Structured JSON Evidence Logging

All major agent invocations, graph state transitions, MCP tool calls, and RAG lookups append structured JSON logs to [evidence/](../evidence/):

- `AC-01_typed_state.json`: Graph state structure schema snapshot.
- `AC-05_checkpointing.json`: State pause/resume thread state log.
- `AC-07_cross_session_memory.json`: Cross-session memory recall proof log.
- `AC-10_mcp_invocation.json`: Tool call parameters, response data, and timestamps.
- `AC-11_agentic_rag.json`: RAG query, retrieved chunk snippets, and relevance scores.
- `AC-12_reflection_trace.json`: Re-planning attempt logs and retry counters.

---

## 2. Trajectory Log Schema

Each step in `ReferralState["logs"]` captures:
```json
{
  "step": "MATCHING_AGENT",
  "status": "MATCHED",
  "matched_specialist_id": "SPC-201",
  "timestamp": "2026-09-06T16:51:15.123456"
}
```

---

## 3. Privacy & Sanitization

- Plaintext patient PII is strictly excluded from execution logs.
- Untrusted provider notes are quarantined prior to logging.
- API keys and environment secrets are never serialized into trace artifacts.
