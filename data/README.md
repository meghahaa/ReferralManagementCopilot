# Synthetic Data Layer for Referral Management Copilot

> [!IMPORTANT]
> **Synthetic Data Notice**: All data in this directory is 100% synthetic and generated strictly for evaluation and development purposes. No real patient, healthcare provider, or Protected Health Information (PHI) is included.

## Directory Structure

```
data/
├── README.md
├── sample_queries.json
├── golden/
│   └── golden_set.jsonl
├── synthetic/
│   ├── referrals.json
│   ├── patients.json
│   ├── providers.json
│   ├── specialists.json
│   ├── eligibility_rules.json
│   └── network_rules.json
└── uploads/
    ├── cardiology_policy.txt
    └── prior_auth_rules.txt
```

## Datasets Overview

### 1. `synthetic/referrals.json`
Contains synthetic referral cases covering 8 major healthcare scenarios:
1. Normal in-network referral (`REF-1001`)
2. Out-of-network referral requiring authorization (`REF-1002`)
3. Urgent referral requiring expedited scheduling (`REF-1003`)
4. Ineligible patient referral (`REF-1004`)
5. Incomplete referral requiring additional intake information (`REF-1005`)
6. Referral requiring complex policy lookup (`REF-1006`)
7. Referral requiring specialist matching (`REF-1007`)
8. Referral requiring automated appointment scheduling (`REF-1008`)

### 2. `synthetic/patients.json`
Synthetic patient demographics, insurance coverage, active plan details, and clinical history.

### 3. `synthetic/providers.json`
Synthetic referring provider profiles, organization affiliations, and contact information.

### 4. `synthetic/specialists.json`
Synthetic specialist profiles, sub-specialties, network status, languages spoken, location, and real-time appointment availability slots.

### 5. `synthetic/eligibility_rules.json` & `synthetic/network_rules.json`
Deterministic eligibility thresholds and network status rules used by tools and agents.

### 6. `uploads/`
Unstructured policy documents (`cardiology_policy.txt`, `prior_auth_rules.txt`) indexed by the Agentic-RAG tool for knowledge retrieval.

### 7. `golden/golden_set.jsonl`
Golden reference benchmark set used by `evals/eval_pipeline.py` to evaluate copilot routing accuracy and structured state extraction.
