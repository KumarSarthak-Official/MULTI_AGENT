from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.models.schemas import ResearchRequest
from app.agents.graph import research_graph
from app.agents.state import ResearchState
import json
import time
import uuid
from typing import AsyncGenerator

router = APIRouter()


async def generate_sse_events(
    research_id: str, query: str, use_documents: bool
) -> AsyncGenerator[str, None]:
    """Generate Server-Sent Events for research execution.

    Args:
        research_id: Unique identifier for this research request
        query: Research topic
        use_documents: Whether to use RAG document retrieval

    Yields:
        SSE formatted strings
    """
    try:
        # Send start event
        yield format_sse_event(
            "start",
            {"research_id": research_id, "query": query, "use_documents": use_documents},
        )

        # Create initial state
        initial_state: ResearchState = {
            "query": query,
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

        # Track execution time
        start_time = time.time()

        # Execute graph
        final_state = research_graph.invoke(initial_state)

        # Send node completion events based on logs
        agent_logs = final_state.get("agent_logs", [])
        current_node = None
        node_logs = []

        for log in agent_logs:
            # Detect node transitions
            if "Search Agent:" in log:
                if current_node and node_logs:
                    yield format_sse_event(
                        "node_complete", {"node": current_node, "logs": node_logs}
                    )
                current_node = "search"
                node_logs = [log]
            elif "RAG Agent:" in log:
                if current_node and node_logs:
                    yield format_sse_event(
                        "node_complete", {"node": current_node, "logs": node_logs}
                    )
                current_node = "rag"
                node_logs = [log]
            elif "Synthesis Agent:" in log:
                if current_node and node_logs:
                    yield format_sse_event(
                        "node_complete", {"node": current_node, "logs": node_logs}
                    )
                current_node = "synthesis"
                node_logs = [log]
            elif "Critique Agent:" in log:
                if current_node and node_logs:
                    yield format_sse_event(
                        "node_complete", {"node": current_node, "logs": node_logs}
                    )
                current_node = "critique"
                node_logs = [log]
            else:
                node_logs.append(log)

        # Send final node completion
        if current_node and node_logs:
            yield format_sse_event(
                "node_complete", {"node": current_node, "logs": node_logs}
            )

        # Calculate duration
        duration = time.time() - start_time

        # Send completion event
        critique = final_state.get("critique", {})
        yield format_sse_event(
            "complete",
            {
                "research_id": research_id,
                "final_report": final_state.get("final_report", ""),
                "sources": final_state.get("sources", []),
                "duration_seconds": round(duration, 2),
                "iteration_count": final_state.get("iteration_count", 0),
                "critique_score": critique.get("score"),
            },
        )

    except Exception as e:
        # Send error event
        yield format_sse_event("error", {"message": str(e), "research_id": research_id})


def format_sse_event(event: str, data: dict) -> str:
    """Format data as Server-Sent Event.

    Args:
        event: Event type
        data: Event payload

    Returns:
        SSE formatted string
    """
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


@router.get("/research/stream")
async def stream_research(query: str, use_documents: bool = True):
    """Stream research execution via Server-Sent Events.

    Args:
        query: Research topic or question
        use_documents: Whether to use RAG document retrieval

    Returns:
        StreamingResponse with SSE events
    """
    research_id = str(uuid.uuid4())

    return StreamingResponse(
        generate_sse_events(research_id, query, use_documents),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )
