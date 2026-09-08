# Drift Detection Strategy

This document outlines strategies for detecting model behavior drift, schema drift, and data distribution drift in the Referral Management Copilot.

---

## 1. Types of Drift Monitored

1. **Schema & Structured Handoff Drift**:
   - Monitored by Pydantic model validation on node boundaries in [schemas.py](../src/referral_copilot/models/schemas.py).
   - If an LLM response fails structural parsing, validation errors trigger the bounded reflection loop in [reflection.py](../src/referral_copilot/agents/reflection.py).

2. **Routing & Topology Drift**:
   - Monitored by evaluating supervisor decision metrics against the golden dataset in [golden_set.jsonl](../data/golden/golden_set.jsonl).

3. **Data & Policy Drift**:
   - Monitored by re-indexing clinical policy documents in [data/uploads/](../data/uploads/) via `scripts/index_rag.py` when clinical directives are updated.

---

## 2. Mitigation Controls

- **Authoritative facts**: Eligibility and specialist/network facts come from the MCP domain tools; model outputs are schema-validated and constrained against those facts.
- **Bounded Reflection**: Recovery attempts are capped at `REFLECTION_MAX_RETRIES` (default `3`) to prevent infinite agent loop execution.
