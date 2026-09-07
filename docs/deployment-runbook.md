# Deployment & Operations Runbook

Step-by-step procedures for deploying, configuring, and operating the Referral Management Copilot.

---

## 1. Local Installation & Configuration

```bash
# 1. Clone repository and navigate to root directory
cd ReferralManagementCopilot

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install pinned dependencies and the package
make install

# 4. Copy configuration template
cp .env.example .env

# 5. Configure provider & API keys in .env
# Set LLM_PROVIDER=gemini or LLM_PROVIDER=groq
# Set GEMINI_API_KEY or GROQ_API_KEY
```

---

## 2. Execution Commands

```bash
# Validate synthetic datasets
make validate

# Index RAG clinical policy documents
make index

# Run full automated test suite
make evidence
make test

# Execute end-to-end referral workflow demo
make demo

# Launch Streamlit interactive web interface
make ui
```

## 3. Docker

```bash
cp .env.example .env
# Add a Gemini or Groq key to .env for live model calls.
make docker-build
make docker-run
```

The container listens on `http://localhost:8501`. It excludes `.env`, local
databases, and the deprecated `vendor/` directory.

---

## 4. Operational Troubleshooting

| Symptom | Cause | Solution |
| :--- | :--- | :--- |
| `ValueError: LIVE API VERIFICATION BLOCKED` | Missing or placeholder API key in `.env` | Set valid `GEMINI_API_KEY` or `GROQ_API_KEY` in `.env`. |
| `Checkpointer requires thread_id` | Missing thread configuration | Provide `config={"configurable": {"thread_id": "YOUR_THREAD_ID"}}` when invoking graph. |
| `UNABLE_TO_MATCH` status | No in-network specialist available | Graph routes automatically to `reflection` node for re-planning. |
