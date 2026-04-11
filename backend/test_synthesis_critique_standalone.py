"""Standalone test for Synthesis and Critique Agents.

Run with: uv run python test_synthesis_critique_standalone.py
"""

from app.agents.state import ResearchState
from app.agents.synthesis_agent import synthesis_agent_node
from app.agents.critique_agent import critique_agent_node


def test_synthesis_and_critique():
    """Test synthesis and critique agents with mock search results."""
    print("Testing Synthesis and Critique Agents...")
    print("=" * 60)

    # Create initial state with mock search results
    state: ResearchState = {
        "query": "What is Retrieval Augmented Generation (RAG)?",
        "messages": [],
        "search_results": [
            {
                "title": "RAG Architecture Explained",
                "url": "https://example.com/rag-architecture",
                "snippet": "RAG combines retrieval and generation to enhance LLM outputs with external knowledge.",
            },
            {
                "title": "Building RAG Systems",
                "url": "https://example.com/building-rag",
                "snippet": "Learn how to build RAG pipelines with vector databases and embeddings.",
            },
            {
                "title": "RAG vs Fine-tuning",
                "url": "https://example.com/rag-vs-finetuning",
                "snippet": "Compare RAG and fine-tuning approaches for customizing LLMs.",
            },
        ],
        "rag_context": [],  # Empty for this test
        "draft_report": None,
        "critique": None,
        "final_report": None,
        "sources": [],
        "agent_logs": [],
        "iteration_count": 0,
        "error": None,
    }

    # Step 1: Run Synthesis Agent
    print("\n" + "-" * 60)
    print("STEP 1: Synthesis Agent")
    print("-" * 60)

    synthesis_result = synthesis_agent_node(state)

    print("\nSynthesis Agent Logs:")
    for log in synthesis_result.get("agent_logs", []):
        print(f"  {log}")

    draft_report = synthesis_result.get("draft_report", "")
    sources = synthesis_result.get("sources", [])

    print(f"\nDraft Report Preview ({len(draft_report)} chars):")
    print("-" * 60)
    print(draft_report[:500] + "..." if len(draft_report) > 500 else draft_report)

    print(f"\nSources ({len(sources)}):")
    for source in sources:
        print(f"  [{source['id']}] {source.get('title', source.get('source', 'Unknown'))}")

    # Update state with synthesis results
    state.update(synthesis_result)

    # Step 2: Run Critique Agent
    print("\n" + "-" * 60)
    print("STEP 2: Critique Agent")
    print("-" * 60)

    critique_result = critique_agent_node(state)

    print("\nCritique Agent Logs:")
    for log in critique_result.get("agent_logs", []):
        print(f"  {log}")

    critique = critique_result.get("critique", {})
    score = critique.get("score", 0)
    feedback = critique.get("feedback", "")

    print(f"\nCritique Score: {score}/10")
    print(f"\nFeedback:")
    print("-" * 60)
    print(feedback[:300] + "..." if len(feedback) > 300 else feedback)

    final_report = critique_result.get("final_report")
    iteration_count = critique_result.get("iteration_count", 0)

    if final_report:
        print("\n" + "=" * 60)
        print(f"SUCCESS: Report finalized with score {score}/10")
        print("=" * 60)
    elif iteration_count > 0:
        print("\n" + "=" * 60)
        print(f"REFINEMENT NEEDED: Score {score}/10, iteration {iteration_count}")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("ERROR: Unexpected state")
        print("=" * 60)


if __name__ == "__main__":
    test_synthesis_and_critique()
