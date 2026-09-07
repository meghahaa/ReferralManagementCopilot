# Referral Management Copilot — Multi-Agent Referrals (AAIE_AGT_011_HLC)

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-orange.svg)](https://github.com/langchain-ai/langgraph)
[![MCP](https://img.shields.io/badge/MCP-SDK-green.svg)](https://modelcontextprotocol.io/)

A stateful, multi-agent healthcare referral management copilot built on **LangGraph**, featuring custom **Model Context Protocol (MCP)** tool integration, **Context Engineering** (Prompt Isolation & Context Compression), **Tiered Memory** with verified cross-session SQLite persistence, and **Agentic-RAG** policy retrieval.

---

## 🌟 Highlights & Key Features

1. **LangGraph Typed Multi-Agent Workflow** (AC-01, AC-02, AC-03):
   - Explicit `ReferralState` TypedDict shared across nodes.
   - Supervisor orchestrator routing referrals across specialized worker agents (`intake`, `eligibility`, `matching`, `scheduling`, `reflection`).
   - Conditional edges handling in-network, out-of-network, urgent SLA, and ineligible referral states.

2. **Centralized LLM Provider Layer**:
   - Centralized LLM Provider Factory (`src/referral_copilot/llm/factory.py`).
   - Easily switch between **Google Gemini** (Default: `LLM_PROVIDER=gemini`) and **Groq** (Optional: `LLM_PROVIDER=groq`) using **one** `.env` configuration value. No Python source code edits required!

3. **Custom MCP Server & Adapter** (AC-09, AC-10):
   - FastMCP server exposing 3 domain tools (`eligibility_check`, `network_lookup`, `specialist_availability`) and 1 resource (`referral_policy://cardiology`).
   - Consumed via `langchain-mcp-adapters` with committed evidence logs.

4. **Context Engineering & Quarantine** (NFR-03, NFR-08):
   - Untrusted free-text referring-provider notes are quarantined in `<UNTRUSTED_REFERRING_PROVIDER_NOTE>` blocks to neutralize prompt injection risks.
   - Context window compression middleware automatically compresses execution logs for long trajectories.

5. **Tiered Memory & Cross-Session Recall** (AC-06, AC-07, AC-08):
   - Short-term working context + Long-term SQLite durable store (`data/memory.db`).
   - Verified cross-session persistence test and committed evidence artifact.
   - Importance-Weighted LRU + TTL Eviction Policy.

6. **Agentic-RAG Policy Lookup** (AC-11):
   - On-demand vector/TF-IDF lookup tool indexing local clinical policy documents.

7. **Reflection & Bounded Self-Healing** (AC-12):
   - Re-planning loop with bounded retry thresholds (default max retries: 3).

---

## 📁 Repository Structure

```
ReferralManagementCopilot/
├── data/                  # Synthetic datasets (referrals, patients, providers, policy docs)
├── docs/                  # Business case, architecture, and AC traceability matrix
├── evals/                 # Evaluation scripts
├── evidence/              # Structured JSON evidence logs (AC-01 through AC-12)
├── scripts/               # Utility scripts (seed, RAG index, evidence generator, demo)
├── src/referral_copilot/  # Core Python package (LLM factory, models, graph, agents, MCP, memory, RAG)
├── tests/                 # Automated pytest suite mapped to AC-01 through AC-12
├── ui/                    # Minimal Streamlit UI application
├── .env.example           # Centralized environment template
├── pyproject.toml         # Package specification
└── README.md              # Documentation quick-start
```

---

## 🚀 Quick-Start Guide

### 1. Environment Setup
```bash
# Set up environment variables
cp .env.example .env

# Configure your preferred LLM provider in .env:
# Default: LLM_PROVIDER=gemini
# Optional: LLM_PROVIDER=groq
```

### 2. Validate Synthetic Datasets
```bash
python scripts/seed_data.py
```

### 3. Run Automated Tests (AC-01 through AC-12)
```bash
pytest
```

### 4. Generate Committed Evidence Artifacts
```bash
python scripts/generate_evidence.py
```

### 5. Run End-to-End Command Line Demo
```bash
python scripts/run_demo.py REF-1001
```

### 6. Launch Minimal Streamlit UI
```bash
streamlit run ui/app.py
```

---

## 🔒 Synthetic Data & Security Compliance
All data contained within this repository is 100% synthetic. No real patient names, social security numbers, or Protected Health Information (PHI) are used.
