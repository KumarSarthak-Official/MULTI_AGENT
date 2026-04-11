from app.agents.state import ResearchState
from app.services.embedding_service import embedding_service
from app.services.llm_service import llm_service
from app.tools.vector_store import vector_store
from typing import Dict, Any


def rag_agent_node(state: ResearchState) -> Dict[str, Any]:
    """RAG Agent: Retrieves relevant documents from vector store with LLM re-ranking.

    Process:
    1. Embed query using nomic-embed-text
    2. Retrieve top-10 documents from Qdrant (cosine similarity, threshold=0.5)
    3. LLM re-ranks chunks 0-10 for relevance
    4. Keep top 6 chunks
    5. Gracefully handle empty collection

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
            limit=10,
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

        # Step 3: LLM re-ranking
        agent_logs.append("RAG Agent: Re-ranking documents with LLM")
        reranked_docs = rerank_documents(query, documents)

        # Step 4: Keep top 6
        top_docs = reranked_docs[:6]
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


def rerank_documents(query: str, documents: list[dict]) -> list[dict]:
    """Re-rank documents using LLM scoring.

    Args:
        query: User query
        documents: List of document dicts from vector search

    Returns:
        Documents sorted by LLM relevance score (highest first)
    """
    system_prompt = """You are a document relevance scorer. Given a query and a document chunk,
score the relevance from 0-10 where:
- 0-3: Not relevant
- 4-6: Somewhat relevant
- 7-8: Relevant
- 9-10: Highly relevant

Return ONLY the numeric score, nothing else."""

    scored_docs = []
    for doc in documents:
        prompt = f"""Query: {query}

Document: {doc['text'][:500]}

Score (0-10):"""

        try:
            response = llm_service.generate(prompt, system_prompt)
            # Extract numeric score
            score_str = response.strip().split()[0]
            score = float(score_str)
        except Exception as e:
            print(f"Error scoring document: {e}")
            score = doc["score"] * 10  # Fallback to vector similarity score

        doc["llm_score"] = score
        scored_docs.append(doc)

    # Sort by LLM score descending
    scored_docs.sort(key=lambda x: x.get("llm_score", 0), reverse=True)
    return scored_docs
