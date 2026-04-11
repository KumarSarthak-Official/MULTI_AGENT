"""Standalone test for RAG Agent.

Run with: uv run python test_rag_standalone.py
"""

from app.agents.state import ResearchState
from app.agents.rag_agent import rag_agent_node
from app.tools.vector_store import vector_store


def test_rag_agent_empty_collection():
    """Test the RAG agent with an empty Qdrant collection."""
    print("Testing RAG Agent with Empty Collection...")
    print("-" * 60)

    # Ensure collection exists (but empty)
    vector_store.ensure_collection()

    # Create initial state
    state: ResearchState = {
        "query": "What is Retrieval Augmented Generation (RAG)?",
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

    # Run RAG agent
    result = rag_agent_node(state)

    # Display logs
    print("\nAgent Logs:")
    for log in result.get("agent_logs", []):
        print(f"  {log}")

    # Display results
    rag_context = result.get("rag_context", [])
    print(f"\nRAG Context ({len(rag_context)} documents):")
    print("-" * 60)

    if rag_context:
        for i, doc in enumerate(rag_context, 1):
            print(f"\n{i}. Source: {doc['source']}")
            print(f"   Score: {doc.get('score', 0):.3f}")
            print(f"   LLM Score: {doc.get('llm_score', 0):.1f}")
            print(f"   Text: {doc['text'][:100]}...")
    else:
        print("\nNo documents in collection (expected for empty collection)")

    # Verify graceful handling
    error = result.get("error")
    if error:
        print("\n" + "=" * 60)
        print(f"ERROR: {error}")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("SUCCESS: RAG agent handled empty collection gracefully")
        print("=" * 60)


if __name__ == "__main__":
    test_rag_agent_empty_collection()
