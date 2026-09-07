# Evaluation Strategy & Benchmark Pipeline

This document defines the evaluation methodology, metrics, and automated benchmark pipeline for the Referral Management Copilot.

---

## 1. Evaluation Architecture

```
[Golden Referral Benchmark Set] ---> (data/golden/golden_set.jsonl)
                  │
                  ▼
       [evals/eval_pipeline.py]
                  │
                  ├──> 1. Graph State Accuracy Score (%)
                  ├──> 2. Routing Precision (%)
                  ├──> 3. Structured Handoff Validation Rate (%)
                  └──> 4. Context Quarantine Compliance Rate (%)
```

---

## 2. Benchmark Datasets

- **Golden Reference Set**: Located in [golden_set.jsonl](file:///home/megha/Documents/Virtusa/Capstone2/ReferralManagementCopilot/data/golden/golden_set.jsonl), containing ground truth expected outcomes across 8 representative referral scenarios:
  1. Routine In-Network Referral (`REF-1001`) $\rightarrow$ `SCHEDULED`
  2. Out-of-Network Referral (`REF-1002`) $\rightarrow$ `OUT_OF_NETWORK_PENDING_AUTH`
  3. Urgent Referral (`REF-1003`) $\rightarrow$ `EXPEDITED_SCHEDULED`
  4. Ineligible Referral (`REF-1004`) $\rightarrow$ `INELIGIBLE`
  5. Incomplete Referral (`REF-1005`) $\rightarrow$ `INTAKE_INCOMPLETE`
  6. Policy Lookup (`REF-1006`) $\rightarrow$ `POLICY_LOOKUP_COMPLETE`
  7. Specialist Match (`REF-1007`) $\rightarrow$ `MATCHED`
  8. Appointment Scheduling (`REF-1008`) $\rightarrow$ `SCHEDULED`

---

## 3. Automated Evaluation Script

The benchmark evaluation pipeline is implemented in [eval_pipeline.py](file:///home/megha/Documents/Virtusa/Capstone2/ReferralManagementCopilot/evals/eval_pipeline.py) and can be executed via:
```bash
python evals/eval_pipeline.py
```
