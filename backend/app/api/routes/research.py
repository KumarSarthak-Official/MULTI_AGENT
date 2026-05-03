from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.models.schemas import ResearchRequest
from app.agents.graph import research_graph
from app.agents.state import ResearchState
from app.models.database import SessionLocal
from app.models.research import Research
from app.models.user import User
from sqlalchemy.exc import OperationalError, SQLAlchemyError
import json
import time
import uuid
import asyncio
from typing import AsyncGenerator
from fastapi import Request, Depends
from app.limiter import limiter
from app.auth import get_current_user

router = APIRouter()


async def generate_sse_events(
    research_id: str, query: str, use_documents: bool, user: User
) -> AsyncGenerator[str, None]:
    """Generate Server-Sent Events for research execution with real-time streaming.

    Uses asyncio.to_thread to run the synchronous LangGraph stream in a
    background thread, relaying events via an asyncio.Queue so SSE events
    are yielded in real-time without blocking the async event loop.

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
            "use_documents": use_documents,
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

        # Attempt to save to database (wrapped in try/except because DB might be offline)
        db = SessionLocal()
        try:
            # Create research record
            db_research = Research(
                id=research_id,
                user_id=user.id,
                query=query,
                use_documents=1 if use_documents else 0,
                status="running"
            )
            db.add(db_research)
            db.commit()
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Warning: Could not save research start to database: {e}")
        finally:
            db.close()

        # Queue to relay events from sync thread to async generator
        event_queue: asyncio.Queue = asyncio.Queue()

        def run_graph_sync():
            """Run the graph in a sync thread, pushing events to the queue."""
            try:
                accumulated_state = dict(initial_state)
                current_node = None
                node_logs = []

                for event in research_graph.stream(initial_state):
                    for node_name, state_update in event.items():
                        events_to_emit = []

                        # Send node start event
                        if node_name != current_node:
                            if current_node and node_logs:
                                events_to_emit.append(
                                    ("node_complete", {"node": current_node, "logs": node_logs})
                                )
                            current_node = node_name
                            node_logs = []
                            events_to_emit.append(
                                ("node_start", {"node": node_name})
                            )

                        # Update accumulated state
                        for key, value in state_update.items():
                            if key == "agent_logs" and isinstance(value, list):
                                existing_logs = accumulated_state.get("agent_logs", [])
                                new_logs = [log for log in value if log not in existing_logs]
                                accumulated_state["agent_logs"] = existing_logs + new_logs

                                for log in new_logs:
                                    node_logs.append(log)
                                    events_to_emit.append(
                                        ("thinking", {"node": node_name, "message": log})
                                    )
                            else:
                                accumulated_state[key] = value

                        for ev_type, ev_data in events_to_emit:
                            event_queue.put_nowait((ev_type, ev_data))

                # Send final node completion
                if current_node and node_logs:
                    event_queue.put_nowait(
                        ("node_complete", {"node": current_node, "logs": node_logs})
                    )

                # Signal completion with final state
                event_queue.put_nowait(("done", accumulated_state))

            except Exception as e:
                event_queue.put_nowait(("graph_error", str(e)))

        # Start graph execution in a background thread
        start_time = time.time()
        graph_task = asyncio.to_thread(run_graph_sync)

        # Create an asyncio task for the thread
        task = asyncio.create_task(graph_task)

        # Relay events from queue to SSE stream in real-time
        while True:
            try:
                # Wait for next event with a small timeout for responsiveness
                ev_type, ev_data = await asyncio.wait_for(
                    event_queue.get(), timeout=300.0  # 5-minute overall timeout
                )
            except asyncio.TimeoutError:
                yield format_sse_event("error", {"message": "Research timed out after 5 minutes", "research_id": research_id})
                task.cancel()
                return

            if ev_type == "done":
                # Send completion event
                accumulated_state = ev_data
                duration = time.time() - start_time
                critique = accumulated_state.get("critique", {})
                
                # Attempt to save final results to database
                db = SessionLocal()
                try:
                    db_research = db.query(Research).filter(Research.id == research_id).first()
                    if db_research:
                        db_research.status = "completed"
                        db_research.final_report = accumulated_state.get("final_report", "")
                        db_research.sources = accumulated_state.get("sources", [])
                        db_research.duration_seconds = round(duration, 2)
                        db_research.iteration_count = accumulated_state.get("iteration_count", 0)
                        db_research.critique_score = critique.get("score")
                        from sqlalchemy.sql import func
                        db_research.completed_at = func.now()
                        db.commit()
                except SQLAlchemyError as e:
                    db.rollback()
                    print(f"Warning: Could not save research results to database: {e}")
                finally:
                    db.close()

                yield format_sse_event(
                    "complete",
                    {
                        "research_id": research_id,
                        "final_report": accumulated_state.get("final_report", ""),
                        "sources": accumulated_state.get("sources", []),
                        "duration_seconds": round(duration, 2),
                        "iteration_count": accumulated_state.get("iteration_count", 0),
                        "critique_score": critique.get("score"),
                    },
                )
                return

            elif ev_type == "graph_error":
                db = SessionLocal()
                try:
                    db_research = db.query(Research).filter(Research.id == research_id).first()
                    if db_research:
                        db_research.status = "failed"
                        db_research.error_message = str(ev_data)
                        db.commit()
                except SQLAlchemyError:
                    db.rollback()
                    pass
                finally:
                    db.close()

                yield format_sse_event("error", {"message": str(ev_data), "research_id": research_id})
                return

            else:
                yield format_sse_event(ev_type, ev_data)

    except Exception as e:
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
@limiter.limit("10/minute")
async def stream_research(
    request: Request,
    query: str,
    use_documents: bool = True,
    user: User = Depends(get_current_user)
):
    """Stream research execution via Server-Sent Events.

    Args:
        query: Research topic or question
        use_documents: Whether to use RAG document retrieval

    Returns:
        StreamingResponse with SSE events
    """
    research_id = str(uuid.uuid4())

    return StreamingResponse(
        generate_sse_events(research_id, query, use_documents, user),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )