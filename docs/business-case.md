# Business Case: Referral Management Copilot (AAIE_AGT_011_HLC)

## 1. Problem Statement
Health systems experience significant administrative friction and care delays in specialist referrals. Up to 30% of specialist referrals suffer from incomplete clinical documentation, wrong-specialty routing, out-of-network leakage, or delayed appointment scheduling.

## 2. Target Workflows & Key Stakeholders
- **Primary Care Physicians (PCPs)**: Submitting electronic specialist referrals with clinical notes.
- **Referral Triage Coordinators**: Verifying insurance coverage, clinical appropriateness, and network compliance.
- **Specialist Clinics**: Managing appointment availability and receiving complete pre-authorized referrals.
- **Patients**: Receiving timely specialist consultations without out-of-network financial surprises.

## 3. Verification Scope

The repository verifies referral status, eligibility, network outcome when a specialist is returned,
required intake fields, policy retrieval, scheduling, quarantine, memory persistence, and bounded recovery
through the automated golden benchmark and acceptance tests. Production turnaround-time and clinical SLA
metrics are outside this synthetic, local capstone scope and are not measured here.
