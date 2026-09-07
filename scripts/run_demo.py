"""End-to-End Command Line Demonstration Script."""

import sys
import json
from referral_copilot.graph.workflow import build_referral_graph
from langgraph.checkpoint.memory import MemorySaver


def run_demo(referral_id: str = "REF-1001"):
    print(f"=== Referral Management Copilot Demo (Referral ID: {referral_id}) ===")
    app = build_referral_graph(checkpointer=MemorySaver())

    initial_state = {
        "referral_id": referral_id,
        "retry_count": 0,
        "logs": []
    }

    config = {"configurable": {"thread_id": f"demo-thread-{referral_id}"}}
    print(f"Executing multi-agent referral workflow for {referral_id}...")

    final_state = app.invoke(initial_state, config=config)

    print("\n---------------------- Execution Summary ----------------------")
    print(f"Referral ID:     {final_state.get('referral_id')}")
    print(f"Final Status:    {final_state.get('status')}")
    if final_state.get("specialist_match"):
        print(f"Matched Doctor:  {final_state['specialist_match'].get('specialist_name')}")
    if final_state.get("scheduling"):
        print(f"Appointment Slot:{final_state['scheduling'].get('appointment_slot')}")
        print(f"Booking ID:      {final_state['scheduling'].get('booking_id')}")

    print("\n---------------------- Graph Execution Trajectory Log ----------------------")
    for idx, log in enumerate(final_state.get("logs", []), 1):
        print(f"{idx}. Step: {log.get('step')} | Status: {log.get('status')}")

    print("\n✓ Demo execution completed cleanly.")


if __name__ == "__main__":
    ref_id = sys.argv[1] if len(sys.argv) > 1 else "REF-1001"
    run_demo(ref_id)
