# OWASP Top 10 for LLM Applications — Compliance Mapping

This document maps the Referral Management Copilot architecture against the OWASP Top 10 Risks for Large Language Model Applications.

---

## OWASP LLM Top 10 Mapping Matrix

| OWASP Vulnerability | Risk Summary | Copilot Defense Mechanism | Implementation File |
| :--- | :--- | :--- | :--- |
| **LLM01: Prompt Injection** | Manipulating LLM via untrusted provider notes. | **Context Quarantine**: Free-text notes wrapped in passive XML blocks. | [quarantine.py](../src/referral_copilot/context/quarantine.py) |
| **LLM02: Sensitive Information Disclosure** | Leaking PII or API secrets in outputs/logs. | **Synthetic Data Guarantee**: 100% synthetic data; zero real PHI. Secrets excluded from trace JSON. | [config.py](../src/referral_copilot/config.py) |
| **LLM03: Supply Chain Risks** | Compromised third-party packages. | Minimal dependencies pinned in [pyproject.toml](../pyproject.toml). | [pyproject.toml](../pyproject.toml) |
| **LLM04: Data and Model Poisoning** | Malicious policy text polluting RAG index. | Controlled indexing of validated local policy documents in `data/uploads/`. | [tool.py](../src/referral_copilot/rag/tool.py) |
| **LLM05: Improper Output Handling** | Unvalidated LLM text driving routing decisions. | **Pydantic Validation**: Structured JSON parsing at all agent handoff boundaries. | [schemas.py](../src/referral_copilot/models/schemas.py) |
| **LLM06: Excessive Agency** | LLM taking unintended autonomous actions. | **Supervisor Graph Topology**: Workflow transitions strictly governed by [router.py](../src/referral_copilot/graph/router.py). | [router.py](../src/referral_copilot/graph/router.py) |
| **LLM07: System Prompt Leakage** | Exposing inner instructions to end user. | Separate user UI layer exposing structured execution status rather than raw prompts. | [app.py](../ui/app.py) |
| **LLM08: Vector and Embedding Weaknesses** | Low-relevance or manipulative RAG retrieval. | FAISS cosine retrieval with configurable `RAG_RELEVANCE_THRESHOLD` (default `0.35`). | [tool.py](../src/referral_copilot/rag/tool.py) |
| **LLM09: Misconfiguration** | Unsecured model endpoints or missing keys. | Centralized provider factory with explicit fallback handling in [factory.py](../src/referral_copilot/llm/factory.py). | [factory.py](../src/referral_copilot/llm/factory.py) |
| **LLM10: Unbounded Consumption** | Infinite loop execution draining API token quota. | **Bounded Reflection**: Retries capped at `REFLECTION_MAX_RETRIES = 3` in [reflection.py](../src/referral_copilot/agents/reflection.py). | [reflection.py](../src/referral_copilot/agents/reflection.py) |
