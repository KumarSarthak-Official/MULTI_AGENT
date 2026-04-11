from langgraph.graph import StateGraph, END
from .state import ResearchState


def build_research_graph():
    """Build the LangGraph StateGraph for the research pipeline.

    The graph will orchestrate 4 agents:
    1. Search Agent - Web search via DuckDuckGo
    2. RAG Agent - Document retrieval from Qdrant
    3. Synthesis Agent - Combine sources into report
    4. Critique Agent - Evaluate and refine (LLM-as-Judge)

    Returns:
        Compiled StateGraph ready for execution
    """
    graph = StateGraph(ResearchState)

    # Nodes will be added as agents are implemented
    # graph.add_node("search", search_agent_node)
    # graph.add_node("rag", rag_agent_node)
    # graph.add_node("synthesis", synthesis_agent_node)
    # graph.add_node("critique", critique_agent_node)

    # Edges will be added after nodes are implemented
    # graph.set_entry_point("search")
    # graph.add_edge("search", "rag")
    # graph.add_edge("rag", "synthesis")
    # graph.add_edge("synthesis", "critique")
    # graph.add_conditional_edges("critique", should_refine)

    return graph.compile()


# Singleton instance (will be initialized after agents are implemented)
# research_graph = build_research_graph()
