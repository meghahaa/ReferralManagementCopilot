# Acceptance Criteria (AC) & NFR Traceability Matrix

Every Acceptance Criterion (AC-01 through AC-12) and Non-Functional Requirement (NFR-01 through NFR-08) is verified by automated tests and committed evidence artifacts.

| ID | Criterion / Requirement | Source Module | Automated Test / Script | Evidence Artifact | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **AC-01** | LangGraph Explicit Typed State | `src/referral_copilot/graph/state.py` | `tests/test_ac_01_typed_state.py` | `evidence/AC-01_typed_state.json` | ✓ PASSED |
| **AC-02** | Supervisor Orchestrator Worker Routing | `src/referral_copilot/graph/supervisor.py` | `tests/test_ac_02_supervisor_routing.py` | `evidence/AC-02_workflow_routing.json` | ✓ PASSED |
| **AC-03** | Conditional Edges Route on State | `src/referral_copilot/graph/router.py` | `tests/test_ac_03_conditional_edges.py` | `evidence/AC-02_workflow_routing.json` | ✓ PASSED |
| **AC-04** | Validated Pydantic Structured Output | `src/referral_copilot/models/schemas.py` | `tests/test_ac_04_structured_output.py` | `evidence/AC-02_workflow_routing.json` | ✓ PASSED |
| **AC-05** | Graph Checkpointer State Persistence | `src/referral_copilot/graph/checkpointer.py` | `tests/test_ac_05_checkpointing.py` | `evidence/AC-05_checkpointing.json` | ✓ PASSED |
| **AC-06** | Tiered Memory System | `src/referral_copilot/memory/tiered.py` | `tests/test_ac_06_tiered_memory.py` | `evidence/AC-07_cross_session_memory.json` | ✓ PASSED |
| **AC-07** | Cross-Session Memory Persistence | `src/referral_copilot/memory/tiered.py` | `tests/test_ac_07_cross_session_memory.py` | `evidence/AC-07_cross_session_memory.json` | ✓ PASSED |
| **AC-08** | Memory Eviction / Importance Policy | `src/referral_copilot/memory/eviction.py` | `tests/test_ac_08_eviction_policy.py` | `evidence/AC-07_cross_session_memory.json` | ✓ PASSED |
| **AC-09** | Custom MCP Server (2 Tools, 1 Resource) | `src/referral_copilot/mcp/server.py` | `tests/test_ac_09_mcp_server.py` | `evidence/AC-10_mcp_invocation.json` | ✓ PASSED |
| **AC-10** | Agent Consumes MCP via Adapter | `src/referral_copilot/mcp/client.py` | `tests/test_ac_10_mcp_client.py` | `evidence/AC-10_mcp_invocation.json` | ✓ PASSED |
| **AC-11** | Agentic-RAG Policy Lookup Tool | `src/referral_copilot/rag/tool.py` | `tests/test_ac_11_agentic_rag.py` | `evidence/AC-11_agentic_rag.json` | ✓ PASSED |
| **AC-12** | Reflection & Self-Healing Fallback | `src/referral_copilot/agents/reflection.py` | `tests/test_ac_12_reflection_self_healing.py` | `evidence/AC-12_reflection_trace.json` | ✓ PASSED |
| **NFR-01**| Environment Variable Config & `.env.example`| `.env.example` | Static Audit | `.env.example` | ✓ PASSED |
| **NFR-02**| Single Documented Quick-Start Command | `scripts/run_demo.py` | Command execution | Demonstration logs | ✓ PASSED |
| **NFR-03**| Untrusted Note Context Quarantine | `src/referral_copilot/context/quarantine.py`| `tests/test_nfr_03_quarantine.py` | `evidence/AC-02_workflow_routing.json` | ✓ PASSED |
| **NFR-04**| Structured JSON Execution Evidence Logs | `scripts/generate_evidence.py` | Evidence audit | `evidence/*.json` | ✓ PASSED |
| **NFR-05**| 100% Synthetic Data Guarantee | `data/synthetic/` | Static Audit | `data/README.md` | ✓ PASSED |
| **NFR-06**| Single-vs-Multi Rationale Documented | `docs/architecture.md` | Doc Audit | `docs/architecture.md` | ✓ PASSED |
| **NFR-07**| Bounded Retries & Fallback Recovery | `src/referral_copilot/agents/reflection.py`| `tests/test_ac_12_reflection_self_healing.py` | `evidence/AC-12_reflection_trace.json` | ✓ PASSED |
| **NFR-08**| Context Summarization Middleware | `src/referral_copilot/context/summarizer.py` | `tests/test_nfr_08_summarization.py` | `evidence/AC-02_workflow_routing.json` | ✓ PASSED |
