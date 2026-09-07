# Compliance & Governance Note

## 1. Regulatory Frameworks & Principles

The Referral Management Copilot is designed with strict adherence to healthcare privacy and governance standards:
- **HIPAA (Health Insurance Portability and Accountability Act)**: Enforces Privacy and Security rules across patient referral processing workflows.
- **Minimum Necessary Standard**: Only clinical and demographic fields required for referral triage, eligibility checking, specialist matching, and scheduling are exposed to worker agents.
- **Synthetic Data Guarantee**: All data used across development, testing, evaluation, and evidence generation is 100% synthetic. No real Protected Health Information (PHI) or Personally Identifiable Information (PII) is present or logged.

---

## 2. Data Isolation & Untrusted Text Quarantine

Free-text notes submitted by external referring providers are treated as **untrusted data**.
- **Quarantine Boundary**: Notes are processed by [quarantine.py](file:///home/megha/Documents/Virtusa/Capstone2/ReferralManagementCopilot/src/referral_copilot/context/quarantine.py) and enclosed within `<UNTRUSTED_REFERRING_PROVIDER_NOTE>` tags.
- **Prompt Injection Defense**: Explicit system instructions prevent the LLM from executing commands or instruction overrides contained within provider notes.

---

## 3. Auditability & Evidence Traceability

- Every execution step, tool call, MCP invocation, RAG query, and graph transition generates structured, deterministic JSON trace evidence in [evidence/](file:///home/megha/Documents/Virtusa/Capstone2/ReferralManagementCopilot/evidence/).
- No secrets, credentials, or real patient identifiers are logged.
