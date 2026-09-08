# Golden Set Design & Benchmark Specification

This document details the schema, coverage, and design rationale behind the benchmark golden dataset.

---

## 1. File Location & Format

- File Path: [golden_set.jsonl](../data/golden/golden_set.jsonl)
- Format: JSON Lines (`.jsonl`)

---

## 2. Test Case Coverage

The golden dataset covers 11 core healthcare referral scenarios:

| Test ID | Referral ID | Patient ID | Specialty | Urgency | Expected Status | Purpose |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `GOLDEN-01` | `REF-1001` | `PAT-001` | Cardiology | ROUTINE | `SCHEDULED` | Normal in-network referral workflow |
| `GOLDEN-02` | `REF-1002` | `PAT-002` | Neurology | ROUTINE | `OUT_OF_NETWORK_PENDING_AUTH` | Out-of-network referral authorization |
| `GOLDEN-03` | `REF-1003` | `PAT-003` | Cardiology | URGENT | `EXPEDITED_SCHEDULED` | Urgent scheduling path |
| `GOLDEN-04` | `REF-1004` | `PAT-004` | Orthopedics | ROUTINE | `INELIGIBLE` | Expired insurance plan rejection |
| `GOLDEN-05` | `REF-1005` | `PAT-005` | Gastroenterology | ROUTINE | `NEEDS_INFO` | Missing mandatory intake clinical fields |
| `GOLDEN-06` | `REF-1006` | `PAT-006` | Cardiology | ROUTINE | `POLICY_LOOKUP_COMPLETE` | Clinical RAG policy lookup |
| `GOLDEN-07` | `REF-1007` | `PAT-007` | Orthopedics | ROUTINE | `SCHEDULED` | Generic in-network match and scheduling |
| `GOLDEN-08` | `REF-1008` | `PAT-008` | Dermatology | ROUTINE | `SCHEDULED` | Real-time slot booking execution |
| `GOLDEN-09` | `REF-1009` | `PAT-002` | Pediatric Neurology | URGENT | `OUT_OF_NETWORK_PENDING_AUTH` | Additional urgent out-of-network case |
| `GOLDEN-10` | `REF-1010` | `PAT-001` | Sleep Medicine | ROUTINE | `FAILED` | Unknown specialty and bounded recovery |
| `GOLDEN-11` | `REF-1011` | `PAT-001` | Cardiology | ROUTINE | `POLICY_LOOKUP_COMPLETE` | Policy lookup with quarantined note |
