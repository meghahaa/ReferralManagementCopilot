# Security: OAuth & Secrets Management Policy

This document defines secrets handling, credential isolation, and environment configuration policies across the repository.

---

## 1. Secrets Management Rules

1. **Zero Committed Secrets (`NFR-01`)**:
   - No production API keys, service tokens, or private credentials may ever be committed to git history.
   - Verified by [.gitignore](../.gitignore) excluding `.env` and SQLite database files.

2. **Centralized Environment Configuration**:
   - Sample environment configuration template is provided in [.env.example](../.env.example).
   - Variables loaded centrally via [config.py](../src/referral_copilot/config.py).

3. **Explicit Placeholders**:
   - All credential values in example templates are formatted as explicit placeholders (`<YOUR_GEMINI_API_KEY>`, `<YOUR_GROQ_API_KEY>`).

4. **Error Handling without Secret Leakage**:
   - When API keys are unconfigured, [factory.py](../src/referral_copilot/llm/factory.py) raises clear exception messages without serializing partially configured key strings.
