"""Test AC-11: Agentic-RAG Policy Retrieval Tool and evidence generation."""

import pytest
from referral_copilot.rag.tool import ReferralPolicyRAGTool
from referral_copilot.config import settings


def test_ac_11_rag_policy_query():
    rag_tool = ReferralPolicyRAGTool()
    res = rag_tool.query_policy("prior authorization requirements for cardiology MRI")

    assert res.relevance_score > 0.0
    assert len(res.retrieved_chunks) > 0
    assert res.policy_source in ["cardiology_policy.txt", "prior_auth_rules.txt"]

    evidence_file = settings.evidence_dir / "AC-11_agentic_rag.json"
    assert evidence_file.exists()
