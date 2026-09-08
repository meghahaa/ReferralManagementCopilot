# Memory System Architecture & Design

This document details the tiered memory system, cross-session persistence mechanisms, and eviction policy implementation.

---

## 1. Tiered Memory Architecture

The Referral Management Copilot employs a two-tier memory architecture:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Short-Term Working Memory (ReferralState TypedDict)     │
│    - Current active referral details, step trajectory logs   │
└──────────────────────────────┬──────────────────────────────┘
                               │ Persists durable facts
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Long-Term Semantic Memory (SQLite Database: memory.db)   │
│    - Cross-session patient preferences, clinical overrides   │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Cross-Session Persistence (`AC-06`, `AC-07`)

- **Storage Engine**: SQLite database located at [data/memory.db](../src/referral_copilot/memory/tiered.py).
- **Verification Test**: Implemented in [test_ac_07_cross_session_memory.py](../tests/test_ac_07_cross_session_memory.py).
  1. `Session A` writes a clinical preference fact.
  2. `Session A` reference is terminated.
  3. `Session B` initializes a new memory store instance and recalls the fact written by `Session A`.

---

## 3. Importance-Weighted LRU Eviction Policy (`AC-08`)

The eviction engine in [eviction.py](../src/referral_copilot/memory/eviction.py) enforces two eviction passes:
1. **TTL Purge**: Expired records (where `created_at + ttl_seconds < now`) are deleted automatically.
2. **Importance-Weighted Capacity Eviction**: When total memory records exceed `max_capacity` ($100$), facts with the lowest `importance_score` and oldest `last_accessed_at` timestamps are evicted first. Facts with `importance_score >= 0.8` (e.g. severe clinical allergies or explicit insurance overrides) are protected from capacity eviction.
