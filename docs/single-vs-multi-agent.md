# Single-Agent vs. Multi-Agent Architecture Rationale

This document documents the evaluation and architectural decision comparing a Single Monolithic Agent architecture against a Supervisor-Worker Multi-Agent architecture.

---

## 1. Architectural Comparison

| Dimension | Single Monolithic Agent | Multi-Agent Supervisor (LangGraph) |
| :--- | :--- | :--- |
| **Domain Isolation** | Poor (Single system prompt handles intake, eligibility, matching, scheduling, and RAG). | High (Dedicated specialized worker nodes for each clinical stage). |
| **State & Control Flow** | Unpredictable (Relies on LLM tool-use loops to decide workflow progression). | Explicit & Typed (`ReferralState` TypedDict with deterministic conditional edges). |
| **Context Window Management** | Bloated (All tool outputs and full conversation history remain in prompt context). | Optimized (Selective context injection & context compression middleware). |
| **Error Recovery** | Hard (Single failure often derails entire agent loop). | Bounded (`reflection` node handles isolated failures with retry caps). |
| **Rule Compliance** | Vulnerable to prompt injection in provider notes. | Isolated (Context Quarantine isolates untrusted free-text notes). |

---

## 2. Selection Rationale

The **Supervisor-Worker Multi-Agent Architecture on LangGraph** was selected because healthcare referral processing demands strict regulatory compliance, deterministic conditional routing (e.g., immediate rejection on expired insurance coverage), and bounded error recovery.
