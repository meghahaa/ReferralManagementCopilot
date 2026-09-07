# Drift Detection Strategy

This document outlines strategies for detecting model behavior drift, schema drift, and data distribution drift in the Referral Management Copilot.

---

## 1. Types of Drift Monitored

1. **Schema & Structured Handoff Drift**:
   - Monitored by Pydantic model validation on node boundaries in [schemas.py](file:///home/megha/Documents/Virtusa/Capstone2/ReferralManagementCopilot/src/referral_copilot/models/schemas.py).
   - If an LLM response fails structural parsing, validation errors trigger the bounded reflection loop in [reflection.py](file:///home/megha/Documents/Virtusa/Capstone2/ReferralManagementCopilot/src/referral_copilot/agents/reflection.py).

2. **Routing & Topology Drift**:
   - Monitored by evaluating supervisor decision metrics against the golden dataset in [golden_set.jsonl](file:///home/megha/Documents/Virtusa/Capstone2/ReferralManagementCopilot/data/golden/golden_set.jsonl).
   - Expected status transitions (e.g., `INTAKE_COMPLETE` $\rightarrow$ `ELIGIBLE` $\rightarrow$ `MATCHED` $\rightarrow$ `SCHEDULED`) are verified deterministically.

3. **Data & Policy Drift**:
   - Monitored by re-indexing clinical policy documents in [data/uploads/](file:///home/megha/Documents/Virtusa/Capstone2/ReferralManagementCopilot/data/uploads/) via `scripts/index_rag.py` when clinical directives are updated.

---

## 2. Mitigation Controls

- **Deterministic Fallbacks**: Crucial edge routing decisions (e.g. out-of-network status or expired insurance rejections) rely on deterministic Python functions in [router.py](file:///home/megha/Documents/Virtusa/Capstone2/ReferralManagementCopilot/src/referral_copilot/graph/router.py) rather than unconstrained model generation.
- **Bounded Reflection**: Re-planning attempts are capped at 3 retries to prevent infinite agent loop execution.
