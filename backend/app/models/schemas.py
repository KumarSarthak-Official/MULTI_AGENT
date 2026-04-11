from pydantic import BaseModel, Field
from typing import Optional, List, Dict


class ResearchRequest(BaseModel):
    """Request model for research endpoint."""

    query: str = Field(..., description="Research topic or question", min_length=1)
    use_documents: bool = Field(
        default=True, description="Whether to use RAG document retrieval"
    )


class ResearchResponse(BaseModel):
    """Response model for completed research."""

    research_id: str
    query: str
    final_report: str
    sources: List[Dict]
    duration_seconds: float
    iteration_count: int
    critique_score: Optional[int] = None


class SSEEvent(BaseModel):
    """Server-Sent Event model."""

    event: str = Field(..., description="Event type: start, node_complete, complete, error")
    data: Dict = Field(..., description="Event payload")


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str
    detail: Optional[str] = None
