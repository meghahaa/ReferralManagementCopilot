# Golden Signals Monitoring Specification

This document defines the 4 Golden Signals (Latency, Traffic, Errors, and Saturation) adapted for multi-agent LLM systems.

---

## 1. The Four Golden Signals

1. **Latency**:
   - Time to complete end-to-end referral triage across graph nodes.
   - Target SLA: $< 2.0$ seconds for deterministic local graph execution; $< 5.0$ seconds when calling live Gemini/Groq providers.

2. **Traffic**:
   - Total volume of active referrals processed per minute.
   - Number of graph state node transitions.

3. **Errors**:
   - Rate of graph state failures (`status == "FAILED"`).
   - Structured parsing validation failures during node output generation.
   - Missing required intake field rejections.

4. **Saturation**:
   - LLM Provider API rate limits and token quota consumption.
   - Memory store capacity utilization in [memory_facts](../src/referral_copilot/memory/tiered.py) (triggers eviction policy when $>100$ records).

---

## 2. Health & Alerting Thresholds

| Signal Metric | Warning Threshold | Critical Threshold | Action Required |
| :--- | :--- | :--- | :--- |
| **Reflection Retry Count** | $\ge 2$ retries | $> 3$ retries | Halt execution and flag case as `FAILED`. |
| **Context Window Depth** | $> 5$ steps | $> 10$ steps | Trigger [summarizer.py](../src/referral_copilot/context/summarizer.py) compression middleware. |
| **API Provider Timeout** | $> 15$ seconds | $> 30$ seconds | Fallback to alternate configured provider or offline rules. |
