"""LangGraph Multi-Agent Workflow Specification.

Satisfies AC-01, AC-02, AC-03, AC-05: Complete graph topology, supervisor orchestrator,
conditional routing, and checkpointing.
"""

from langgraph.graph import StateGraph, START, END
from referral_copilot.graph.state import ReferralState
from referral_copilot.graph.supervisor import supervisor_agent_node
from referral_copilot.agents.intake import intake_agent_node
from referral_copilot.agents.eligibility import eligibility_agent_node
from referral_copilot.agents.matching import matching_agent_node
from referral_copilot.agents.scheduling import scheduling_agent_node
from referral_copilot.agents.reflection import reflection_agent_node
from referral_copilot.graph.router import route_next
from referral_copilot.graph.checkpointer import get_sqlite_checkpointer


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

    workflow.add_conditional_edges("supervisor", route_next, routing_map)
    workflow.add_conditional_edges("intake", route_next, routing_map)
    workflow.add_conditional_edges("eligibility", route_next, routing_map)
    workflow.add_conditional_edges("matching", route_next, routing_map)
    workflow.add_conditional_edges("scheduling", route_next, routing_map)
    workflow.add_conditional_edges("reflection", route_next, routing_map)

    cp = checkpointer if checkpointer is not None else get_sqlite_checkpointer()
    return workflow.compile(checkpointer=cp)
