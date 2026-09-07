# Security: PII / PHI Redaction & Synthetic Data Policy

This document defines the PII/PHI sanitization and synthetic data policy across all repository datasets, scripts, logs, and evidence files.

---

## 1. 100% Synthetic Data Guarantee (`NFR-05`)

- **Zero Real PHI**: No real patient medical records, actual social security numbers, real phone numbers, or genuine provider NPIs are present in this repository.
- **Synthetic Identifiers**: All identifiers follow explicit synthetic patterns:
  - Patient IDs: `PAT-001`, `PAT-002`
  - Referral IDs: `REF-1001`, `REF-1002`
  - Provider IDs: `PRV-101`, `PRV-102`
  - Specialist IDs: `SPC-201`, `SPC-202`
  - Patient Names: `Jane Doe (Synthetic)`, `John Smith (Synthetic)`

---

## 2. Redaction & Logging Controls

1. **Structured Trace Filtering**: Log outputs in [evidence/](file:///home/megha/Documents/Virtusa/Capstone2/ReferralManagementCopilot/evidence/) serialize synthetic identifiers only (`PAT-001`, `REF-1001`).
2. **Quarantine Isolation**: Untrusted free-text referring-provider notes are isolated to prevent un-redacted user text from contaminating trusted LLM system instructions.
3. **Database Privacy**: Local SQLite databases (`data/checkpoints.db`, `data/memory.db`) store synthetic referral state and are excluded from git tracking in [.gitignore](file:///home/megha/Documents/Virtusa/Capstone2/ReferralManagementCopilot/.gitignore).
