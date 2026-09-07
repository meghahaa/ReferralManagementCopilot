# Deployment Readiness Checklist

This checklist defines the production readiness gates for the Referral Management Copilot repository.

---

## Readiness Gates & Checklist

- [x] **Python Environment**: Target runtime Python 3.11+ specified in [pyproject.toml](file:///home/megha/Documents/Virtusa/Capstone2/ReferralManagementCopilot/pyproject.toml).
- [x] **No Docker / No External Database Requirement**: System builds and executes via standard Python pip toolchain with SQLite local checkpointing.
- [x] **Zero Hardcoded Secrets**: Credentials managed via environment variables; [.env.example](file:///home/megha/Documents/Virtusa/Capstone2/ReferralManagementCopilot/.env.example) committed; no API keys committed to repository.
- [x] **Centralized LLM Factory**: Provider switching configured centrally in [factory.py](file:///home/megha/Documents/Virtusa/Capstone2/ReferralManagementCopilot/src/referral_copilot/llm/factory.py) (`LLM_PROVIDER=gemini` or `LLM_PROVIDER=groq`).
- [x] **Synthetic Data Compliance**: 100% synthetic datasets in [data/synthetic/](file:///home/megha/Documents/Virtusa/Capstone2/ReferralManagementCopilot/data/synthetic/); no real patient PHI.
- [x] **Automated Test Suite**: 15 unit/integration tests covering AC-01 through AC-12 passing cleanly (`pytest tests/`).
- [x] **Evidence Generation**: Execution evidence JSON artifacts committed in [evidence/](file:///home/megha/Documents/Virtusa/Capstone2/ReferralManagementCopilot/evidence/).
- [x] **Custom MCP Server**: FastMCP server exposing 3 tools and 1 resource in [server.py](file:///home/megha/Documents/Virtusa/Capstone2/ReferralManagementCopilot/src/referral_copilot/mcp/server.py).
- [x] **Tiered Memory Persistence**: Cross-session memory recall verified in [test_ac_07_cross_session_memory.py](file:///home/megha/Documents/Virtusa/Capstone2/ReferralManagementCopilot/tests/test_ac_07_cross_session_memory.py).
- [x] **Single-Command Reproducibility**: Runnable via `python scripts/run_demo.py REF-1001`.
