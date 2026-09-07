# Deployment & Operations Runbook

Step-by-step procedures for deploying, configuring, and operating the Referral Management Copilot.

---

## 1. Local Installation & Configuration

```bash
# 1. Clone repository and navigate to root directory
cd ReferralManagementCopilot

# 2. Copy configuration template
cp .env.example .env

# 3. Configure provider & API keys in .env
# Set LLM_PROVIDER=gemini or LLM_PROVIDER=groq
# Set GEMINI_API_KEY or GROQ_API_KEY
```

---

## 2. Execution Commands

```bash
# Validate synthetic datasets
python scripts/seed_data.py

# Index RAG clinical policy documents
python scripts/index_rag.py

# Run full automated test suite
python scripts/generate_evidence.py
pytest tests/

# Execute end-to-end referral workflow demo
python scripts/run_demo.py REF-1001

# Launch Streamlit interactive web interface
streamlit run ui/app.py
```

---

## 3. Operational Troubleshooting

| Symptom | Cause | Solution |
| :--- | :--- | :--- |
| `ValueError: LIVE API VERIFICATION BLOCKED` | Missing or placeholder API key in `.env` | Set valid `GEMINI_API_KEY` or `GROQ_API_KEY` in `.env`. |
| `Checkpointer requires thread_id` | Missing thread configuration | Provide `config={"configurable": {"thread_id": "YOUR_THREAD_ID"}}` when invoking graph. |
| `UNABLE_TO_MATCH` status | No in-network specialist available | Graph routes automatically to `reflection` node for re-planning. |
