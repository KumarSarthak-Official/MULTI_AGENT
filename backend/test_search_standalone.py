"""Standalone test for Search Agent.

Run with: uv run python test_search_standalone.py
"""

from app.agents.state import ResearchState
from app.agents.search_agent import search_agent_node


def test_search_agent():
    """Test the search agent with a sample query."""
    print("Testing Search Agent...")
    print("-" * 60)

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

    # Run search agent
    result = search_agent_node(state)

    # Display logs
    print("\nAgent Logs:")
    for log in result.get("agent_logs", []):
        print(f"  {log}")

    # Display results
    search_results = result.get("search_results", [])
    print(f"\nSearch Results ({len(search_results)} found):")
    print("-" * 60)

    for i, result_item in enumerate(search_results, 1):
        print(f"\n{i}. {result_item['title']}")
        print(f"   URL: {result_item['url']}")
        print(f"   Snippet: {result_item['snippet'][:100]}...")

    # Verify success
    if search_results:
        print("\n" + "=" * 60)
        print("SUCCESS: Search agent returned results")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("WARNING: No search results returned")
        print("=" * 60)


if __name__ == "__main__":
    test_search_agent()
