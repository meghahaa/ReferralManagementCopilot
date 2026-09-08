"""LangGraph Multi-Agent Workflow Specification.

Satisfies AC-01, AC-02, AC-03, AC-05: Complete graph topology, supervisor orchestrator,
conditional routing, and checkpointing.
"""

import json
from datetime import datetime, timezone

from langgraph.graph import StateGraph, START, END
from referral_copilot.graph.state import ReferralState
from referral_copilot.graph.supervisor import supervisor_agent_node
from referral_copilot.agents.intake import intake_agent_node
from referral_copilot.agents.eligibility import eligibility_agent_node
from referral_copilot.agents.matching import matching_agent_node
from referral_copilot.agents.scheduling import scheduling_agent_node
from referral_copilot.agents.reflection import reflection_agent_node
from referral_copilot.graph.router import route_after_context, route_from_supervisor
from referral_copilot.graph.checkpointer import get_sqlite_checkpointer
from referral_copilot.config import settings
from referral_copilot.context.summarizer import compress_context


class EvidenceGraph:
    """Compiled graph facade that records every invoke as an append-only trace."""

    def __init__(self, graph):
        self._graph = graph

    def invoke(self, input_state, config=None, **kwargs):
        result = self._graph.invoke(input_state, config=config, **kwargs)
        self._record_run(result, config)
        return result

    def _record_run(self, result, config):
        evidence_file = settings.evidence_dir / "AC-02_workflow_routing.json"
        runs = []
        if evidence_file.exists():
            try:
                existing = json.loads(evidence_file.read_text(encoding="utf-8"))
                runs = existing if isinstance(existing, list) else [existing]
            except (OSError, json.JSONDecodeError):
                runs = []

        thread_id = ((config or {}).get("configurable") or {}).get("thread_id")
        runs.append({
            "ac_id": "AC-02",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "thread_id": thread_id,
            "referral_id": result.get("referral_id"),
            "final_status": result.get("status"),
            "trajectory": result.get("logs", []),
        })
        evidence_file.write_text(json.dumps(runs, indent=2), encoding="utf-8")

    def __getattr__(self, name):
        return getattr(self._graph, name)


def context_compression_node(state: ReferralState) -> ReferralState:
    """Apply context compression between worker cycles and supervisor decisions."""
    return compress_context(state)


def build_referral_graph(checkpointer=None):
    """Constructs and compiles the Referral Copilot LangGraph workflow.

    Args:
        checkpointer: Optional LangGraph checkpointer instance.

    Returns:
        Compiled StateGraph runnable application.
    """
    workflow = StateGraph(ReferralState)

    # Add Nodes
    workflow.add_node("supervisor", supervisor_agent_node)
    workflow.add_node("intake", intake_agent_node)
    workflow.add_node("eligibility", eligibility_agent_node)
    workflow.add_node("matching", matching_agent_node)
    workflow.add_node("scheduling", scheduling_agent_node)
    workflow.add_node("reflection", reflection_agent_node)
    workflow.add_node("context_compression", context_compression_node)

    # Add Edges
    workflow.add_edge(START, "supervisor")

    # Conditional Routing Edges
    routing_map = {
        "intake": "intake",
        "eligibility": "eligibility",
        "matching": "matching",
        "scheduling": "scheduling",
        "reflection": "reflection",
        "__end__": END
    }
    context_routing_map = {"supervisor": "supervisor", "__end__": END}

    workflow.add_conditional_edges("supervisor", route_from_supervisor, routing_map)
    for worker in ("intake", "eligibility", "matching", "scheduling", "reflection"):
        workflow.add_edge(worker, "context_compression")
    workflow.add_conditional_edges("context_compression", route_after_context, context_routing_map)

    cp = checkpointer if checkpointer is not None else get_sqlite_checkpointer()
    return EvidenceGraph(workflow.compile(checkpointer=cp))
