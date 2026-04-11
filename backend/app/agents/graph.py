from langgraph.graph import StateGraph, END
from .state import ResearchState
from .search_agent import search_agent_node
from .rag_agent import rag_agent_node
from .synthesis_agent import synthesis_agent_node
from .critique_agent import critique_agent_node


def should_refine(state: ResearchState) -> str:
    """Conditional edge function to decide if report needs refinement.

    Logic:
    - If iterations >= 2: END (max iterations reached)
    - If score < 7: return "synthesis" (trigger refinement)
    - Otherwise: END (score is good)

    Args:
        state: Current ResearchState

    Returns:
        Next node name ("synthesis") or END
    """
    critique = state.get("critique", {})
    score = critique.get("score", 10)
    iteration_count = state.get("iteration_count", 0)

    # Check if max iterations reached
    if iteration_count >= 2:
        # Ensure final_report is set
        if not state.get("final_report"):
            state["final_report"] = state.get("draft_report", "")
        return END

    # Check if score is below threshold
    if score < 7:
        return "synthesis"

    # Score is good, finalize
    if not state.get("final_report"):
        state["final_report"] = state.get("draft_report", "")
    return END


def build_research_graph():
    """Build the LangGraph StateGraph for the research pipeline.

    The graph orchestrates 4 agents:
    1. Search Agent - Web search via DuckDuckGo
    2. RAG Agent - Document retrieval from Qdrant
    3. Synthesis Agent - Combine sources into report
    4. Critique Agent - Evaluate and refine (LLM-as-Judge)

    Graph flow:
    Entry → search → rag → synthesis → critique
                              ↑           |
                              └─(score<7)─┘

    Returns:
        Compiled StateGraph ready for execution
    """
    graph = StateGraph(ResearchState)

    # Add agent nodes
    graph.add_node("search", search_agent_node)
    graph.add_node("rag", rag_agent_node)
    graph.add_node("synthesis", synthesis_agent_node)
    graph.add_node("critique", critique_agent_node)

    # Set entry point
    graph.set_entry_point("search")

    # Add sequential edges
    graph.add_edge("search", "rag")
    graph.add_edge("rag", "synthesis")
    graph.add_edge("synthesis", "critique")

    # Add conditional edge from critique
    graph.add_conditional_edges(
        "critique",
        should_refine,
        {
            "synthesis": "synthesis",
            END: END,
        },
    )

    return graph.compile()


# Singleton instance
research_graph = build_research_graph()
