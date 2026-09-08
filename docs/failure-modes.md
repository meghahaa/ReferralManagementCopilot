# Failure Modes & Recovery Strategies

This document categorizes failure modes, degradation paths, and recovery strategies in the Referral Management Copilot.

---

## Failure Matrix & Recovery Paths

| Failure Category | Specific Failure Trigger | Circuit Breaker / Recovery Mechanism | Fallback State |
| :--- | :--- | :--- | :--- |
| **API / Provider Failure** | LLM API timeout or missing API key credentials | `get_llm()` raises explicit `ValueError: LIVE API VERIFICATION BLOCKED` informing user of missing `.env` key. | Deterministic fallback nodes execute standard rule validation without crash. |
| **Tool Execution Failure** | MCP tool invocation exception or invalid output | Worker catches the exception, records a safe error category, marks `TOOL_FAILURE`, and routes to `reflection`. | Bounded retry or termination after the configured retry limit. |
| **Data Incompleteness** | Referral missing target specialty, ICD-10 code, or clinical reason | Detected during Intake agent execution in [intake.py](../src/referral_copilot/agents/intake.py). | Workflow routed immediately to `INTAKE_INCOMPLETE` terminal state. |
| **Insurance Ineligibility** | Patient policy coverage status `EXPIRED` | Detected by MCP `eligibility_check` tool in [eligibility.py](../src/referral_copilot/agents/eligibility.py). | Workflow routed immediately to `INELIGIBLE` terminal state. |
| **Out-of-Network Referral** | Specialist matched is out-of-network without pre-approval | Detected by Specialist Matching agent in [matching.py](../src/referral_copilot/agents/matching.py). | Workflow routed to `OUT_OF_NETWORK_PENDING_AUTH` terminal state. |
| **Infinite Re-planning Loop** | Specialist matching or scheduling failing repeatedly | Bounded retry counter in [reflection.py](../src/referral_copilot/agents/reflection.py). | Capped at `REFLECTION_MAX_RETRIES = 3` before forcing state to `FAILED`. |
