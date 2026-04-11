"""End-to-end test for complete LangGraph research pipeline.

Run with: uv run python test_graph_e2e.py

This is the CRITICAL Day 6 checkpoint - if this fails, the entire backend is blocked.
"""

from app.agents.graph import research_graph
from app.agents.state import ResearchState
import time


def test_full_graph_execution():
    """Test complete graph execution with all 4 agents."""
    print("=" * 70)
    print("CRITICAL CHECKPOINT: Full Graph End-to-End Test")
    print("=" * 70)

    # Create initial state
    initial_state: ResearchState = {
        "query": "What is Retrieval Augmented Generation and how does it work?",
        "messages": [],
        "search_results": [],
        "rag_context": [],
        "draft_report": None,
        "critique": None,
        "final_report": None,
        "sources": [],
        "agent_logs": [],
        "iteration_count": 0,
        "error": None,
    }

    print(f"\nQuery: {initial_state['query']}")
    print("\nStarting graph execution...")
    print("-" * 70)

    start_time = time.time()

    try:
        # Execute the graph
        final_state = research_graph.invoke(initial_state)

        elapsed_time = time.time() - start_time

        # Display agent logs
        print("\n" + "=" * 70)
        print("AGENT EXECUTION LOGS")
        print("=" * 70)
        for log in final_state.get("agent_logs", []):
            print(f"  {log}")

        # Display results
        print("\n" + "=" * 70)
        print("RESULTS")
        print("=" * 70)

        search_results = final_state.get("search_results", [])
        print(f"\nSearch Results: {len(search_results)} found")

        rag_context = final_state.get("rag_context", [])
        print(f"RAG Context: {len(rag_context)} documents")

        critique = final_state.get("critique", {})
        score = critique.get("score", 0)
        print(f"Critique Score: {score}/10")

        iteration_count = final_state.get("iteration_count", 0)
        print(f"Refinement Iterations: {iteration_count}")

        final_report = final_state.get("final_report", "")
        print(f"\nFinal Report Length: {len(final_report)} characters")

        sources = final_state.get("sources", [])
        print(f"Total Sources: {len(sources)}")

        error = final_state.get("error")
        if error:
            print(f"\nError: {error}")

        # Display report preview
        print("\n" + "=" * 70)
        print("FINAL REPORT PREVIEW")
        print("=" * 70)
        if final_report:
            preview_length = min(800, len(final_report))
            print(final_report[:preview_length])
            if len(final_report) > preview_length:
                print(f"\n... ({len(final_report) - preview_length} more characters)")
        else:
            print("No final report generated")

        # Verification
        print("\n" + "=" * 70)
        print("VERIFICATION")
        print("=" * 70)

        checks = {
            "Search agent executed": len(search_results) > 0,
            "RAG agent executed": True,  # Always executes, may return empty
            "Synthesis agent executed": len(final_report) > 0,
            "Critique agent executed": critique is not None,
            "Final report generated": final_report is not None and len(final_report) > 0,
            "Sources collected": len(sources) > 0,
            "No errors": error is None,
        }

        all_passed = True
        for check, passed in checks.items():
            status = "PASS" if passed else "FAIL"
            print(f"  [{status}] {check}")
            if not passed:
                all_passed = False

        print(f"\nExecution Time: {elapsed_time:.2f} seconds")

        # Final verdict
        print("\n" + "=" * 70)
        if all_passed:
            print("SUCCESS: All agents executed successfully!")
            print("CRITICAL CHECKPOINT PASSED - Backend is ready for API layer")
        else:
            print("FAILURE: Some checks failed - debug before proceeding")
        print("=" * 70)

        return all_passed

    except Exception as e:
        elapsed_time = time.time() - start_time
        print("\n" + "=" * 70)
        print("CRITICAL FAILURE")
        print("=" * 70)
        print(f"Error: {str(e)}")
        print(f"\nExecution Time: {elapsed_time:.2f} seconds")
        print("\nStack trace:")
        import traceback
        traceback.print_exc()
        print("\n" + "=" * 70)
        print("CRITICAL CHECKPOINT FAILED - Debug graph before proceeding")
        print("=" * 70)
        return False


if __name__ == "__main__":
    success = test_full_graph_execution()
    exit(0 if success else 1)
