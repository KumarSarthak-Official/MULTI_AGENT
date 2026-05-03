from app.agents.state import ResearchState
from app.services.embedding_service import embedding_service
from app.tools.vector_store import vector_store
from typing import Dict, Any


def rag_agent_node(state: ResearchState) -> Dict[str, Any]:
    """RAG Agent: Retrieves relevant documents from vector store.

    Process:
    1. Embed query using nomic-embed-text
    2. Retrieve top-6 documents from Qdrant (cosine similarity, threshold=0.5)
    3. Keep top 4 by vector similarity score
    4. Gracefully handle empty collection

    Args:
        state: Current ResearchState

    Returns:
        Dict with updated rag_context and agent_logs
    """
    query = state["query"]
    agent_logs = [f"RAG Agent: Starting document retrieval for '{query}'"]

    try:
        # Step 1: Embed query
        agent_logs.append("RAG Agent: Generating query embedding")
        query_vector = embedding_service.embed_query(query)

        # Step 2: Retrieve from Qdrant
        agent_logs.append("RAG Agent: Querying vector store")
        documents = vector_store.query_documents(
            query_vector=query_vector,
            limit=6,  # Reduced from 10 to 6
            score_threshold=0.5,
        )

        # Handle empty collection
        if not documents:
            agent_logs.append("RAG Agent: No documents found in vector store")
            return {
                "rag_context": [],
                "agent_logs": agent_logs,
            }

        agent_logs.append(f"RAG Agent: Retrieved {len(documents)} documents")

        # Skip LLM re-ranking for speed - use vector similarity scores directly
        agent_logs.append("RAG Agent: Using vector similarity scores")

        # Documents are already sorted by score from Qdrant
        top_docs = documents[:4]  # Keep top 4 instead of 6
        agent_logs.append(f"RAG Agent: Returning top {len(top_docs)} documents")

        return {
            "rag_context": top_docs,
            "agent_logs": agent_logs,
        }

    except Exception as e:
        error_msg = f"RAG Agent: Error - {str(e)}"
        agent_logs.append(error_msg)
        return {
            "rag_context": [],
            "agent_logs": agent_logs,
            "error": error_msg,
        }
