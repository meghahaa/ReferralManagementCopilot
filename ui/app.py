"""Streamlit Minimal UI for Referral Management Copilot."""

import streamlit as st
import json
from pathlib import Path
from referral_copilot.graph.workflow import build_referral_graph
from langgraph.checkpoint.memory import MemorySaver
from referral_copilot.memory.tiered import TieredMemoryStore
from referral_copilot.rag.tool import ReferralPolicyRAGTool

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

st.set_page_config(page_title="Referral Management Copilot", layout="wide")

st.title("🏥 Referral Management Copilot")
st.caption("Multi-Agent Healthcare Specialist Referral System (LangGraph + MCP + Context Engineering + Tiered Memory)")

# Sidebar Configuration
st.sidebar.header("Configuration & Control")
selected_ref_id = st.sidebar.selectbox(
    "Select Synthetic Referral Case",
    ["REF-1001", "REF-1002", "REF-1003", "REF-1004", "REF-1005", "REF-1006", "REF-1007", "REF-1008"]
)

if st.sidebar.button("Run Multi-Agent Referral Graph", type="primary"):
    with st.spinner("Executing LangGraph multi-agent referral graph..."):
        app = build_referral_graph(checkpointer=MemorySaver())
        config = {"configurable": {"thread_id": f"ui-thread-{selected_ref_id}"}}
        initial_state = {"referral_id": selected_ref_id, "retry_count": 0, "logs": []}
        final_state = app.invoke(initial_state, config=config)

        st.session_state["graph_result"] = final_state

if "graph_result" in st.session_state:
    res = st.session_state["graph_result"]
    col1, col2, col3 = st.columns(3)
    col1.metric("Referral ID", res.get("referral_id"))
    col2.metric("Final Status", res.get("status"))
    col3.metric("Urgency", (res.get("referral") or {}).get("urgency", "ROUTINE"))

    st.subheader("Graph Execution Trajectory")
    st.json(res.get("logs", []))

    st.subheader("Specialist & Scheduling Handoff")
    st.write("**Matched Specialist:**", res.get("specialist_match"))
    st.write("**Scheduling Record:**", res.get("scheduling"))

    if res.get("quarantined_note"):
        st.warning("Quarantined Referring Provider Free-Text Note (Isolated)")
        st.code(res.get("quarantined_note"))

# Policy RAG Search Tab
st.divider()
st.subheader("🔍 Clinical Policy Agentic-RAG Search")
query = st.text_input("Query referral policy database", "Cardiology prior authorization rules")
if st.button("Search Policy"):
    tool = ReferralPolicyRAGTool()
    rag_res = tool.query_policy(query)
    st.write(f"**Relevance Score:** {rag_res.relevance_score} | **Source:** `{rag_res.policy_source}`")
    st.json(rag_res.retrieved_chunks)
