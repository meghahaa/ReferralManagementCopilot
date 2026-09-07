# Golden Set Design & Benchmark Specification

This document details the schema, coverage, and design rationale behind the benchmark golden dataset.

---

## 1. File Location & Format

- File Path: [golden_set.jsonl](file:///home/megha/Documents/Virtusa/Capstone2/ReferralManagementCopilot/data/golden/golden_set.jsonl)
- Format: JSON Lines (`.jsonl`)

---

## 2. Test Case Coverage

The golden dataset covers 8 core healthcare referral scenarios:

| Test ID | Referral ID | Patient ID | Specialty | Urgency | Expected Status | Purpose |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `GOLDEN-01` | `REF-1001` | `PAT-001` | Cardiology | ROUTINE | `SCHEDULED` | Normal in-network referral workflow |
| `GOLDEN-02` | `REF-1002` | `PAT-002` | Neurology | ROUTINE | `OUT_OF_NETWORK_PENDING_AUTH` | Out-of-network referral authorization |
| `GOLDEN-03` | `REF-1003` | `PAT-003` | Cardiology | URGENT | `EXPEDITED_SCHEDULED` | Priority scheduling within 24h SLA |
| `GOLDEN-04` | `REF-1004` | `PAT-004` | Orthopedics | ROUTINE | `INELIGIBLE` | Expired insurance plan rejection |
| `GOLDEN-05` | `REF-1005` | `PAT-005` | Gastroenterology | ROUTINE | `NEEDS_INFO` | Missing mandatory intake clinical fields |
| `GOLDEN-06` | `REF-1006` | `PAT-006` | Cardiology | ROUTINE | `POLICY_LOOKUP_COMPLETE` | Clinical RAG policy lookup |
| `GOLDEN-07` | `REF-1007` | `PAT-007` | Orthopedics | ROUTINE | `MATCHED` | Specialist matching node execution |
| `GOLDEN-08` | `REF-1008` | `PAT-008` | Dermatology | ROUTINE | `SCHEDULED` | Real-time slot booking execution |
