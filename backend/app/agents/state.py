from typing import TypedDict, Annotated, List, Optional
from langchain_core.messages import BaseMessage
import operator


class ResearchState(TypedDict):
    """Shared state for the research agent graph.

    This state is passed between all agent nodes and accumulates information
    as the research process progresses through search, RAG, synthesis, and critique.
    """

    # Input
    query: str

    # Messages for LLM conversation history
    messages: Annotated[List[BaseMessage], operator.add]

    # Search agent results
    search_results: List[dict]  # [{title, url, snippet}]

    # RAG agent results
    rag_context: List[dict]  # [{text, source, score}]

    # Synthesis agent output
    draft_report: Optional[str]

    # Critique agent output
    critique: Optional[dict]  # {score: int, feedback: str}

    # Final output
    final_report: Optional[str]

    # All sources (web + documents)
    sources: List[dict]

    # Agent execution logs for debugging and UI display
    agent_logs: Annotated[List[str], operator.add]

    # Iteration counter for critique loop
    iteration_count: int

    # Error tracking
    error: Optional[str]
