"""
Per-Agent RAGAS Evaluation
============================
Evaluate each LangGraph agent independently to pinpoint
exactly which stage is underperforming.

Agents evaluated:
  • RAG Agent       → context_recall + context_precision
  • Synthesis Agent → faithfulness
"""

import asyncio
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import ContextRecall, ContextPrecision, Faithfulness

from app.evaluation.config import eval_llm
from app.tools.vector_store import vector_store
from app.services.embedding_service import embedding_service
from app.agents.graph import research_graph


# --------------------------------------------------------------------------
# RAG Agent: does Qdrant return the RIGHT chunks?
# --------------------------------------------------------------------------
def evaluate_rag_agent(questions: list[str]) -> dict:
    """
    Evaluate ONLY the Qdrant retrieval step (RAG Agent).
    Metrics: context_recall + context_precision.

    Requires a 'reference' answer to score context_recall correctly.
    We use the question itself as a proxy reference if none is provided.
    """
    samples: list[dict] = []
    for q in questions:
        try:
            query_vector = embedding_service.embed_query(q)
            docs = vector_store.query_documents(
                query_vector=query_vector,
                limit=5,
                score_threshold=0.4,
            )
            contexts = [d["text"] for d in docs if d.get("text")]
            samples.append(
                {
                    "user_input": q,
                    "retrieved_contexts": contexts or [""],
                    "response": "N/A",   # not needed for context-only metrics
                    "reference": q,      # proxy — replace with real ground-truth
                }
            )
        except Exception as e:
            print(f"  ⚠️  RAG retrieval failed for '{q}': {e}")

    if not samples:
        return {"rag_agent": {"error": "No samples collected"}}

    dataset = Dataset.from_list(samples)
    results = evaluate(
        dataset=dataset,
        metrics=[
            ContextRecall(llm=eval_llm),
            ContextPrecision(llm=eval_llm),
        ],
        llm=eval_llm,
        raise_exceptions=False,
    )

    cr = float(results["context_recall"])
    cp = float(results["context_precision"])
    return {
        "rag_agent": {
            "context_recall":    round(cr, 4),
            "context_precision": round(cp, 4),
            "verdict": (
                "✅ Good retrieval"
                if cr > 0.75
                else "⚠️  Improve chunking / embeddings"
            ),
        }
    }


# --------------------------------------------------------------------------
# Synthesis Agent: does the LLM hallucinate?
# --------------------------------------------------------------------------
def evaluate_synthesis_agent(questions: list[str]) -> dict:
    """
    Evaluate ONLY the synthesis agent (faithfulness).
    Runs the full pipeline but scores only the synthesis output vs contexts.
    """
    samples: list[dict] = []
    for q in questions:
        try:
            state = research_graph.invoke(
                {
                    "query": q,
                    "use_documents": True,
                    "messages": [],
                    "search_results": [],
                    "rag_context": [],
                    "sources": [],
                    "agent_logs": [],
                    "iteration_count": 0,
                }
            )
            response = state.get("final_report") or state.get("draft_report") or ""
            contexts = [
                c.get("text", "")
                for c in state.get("rag_context", [])
                if c.get("text")
            ]
            samples.append(
                {
                    "user_input": q,
                    "response": response,
                    "retrieved_contexts": contexts or [""],
                    "reference": "",
                }
            )
        except Exception as e:
            print(f"  ⚠️  Pipeline failed for '{q}': {e}")

    if not samples:
        return {"synthesis_agent": {"error": "No samples collected"}}

    dataset = Dataset.from_list(samples)
    results = evaluate(
        dataset=dataset,
        metrics=[Faithfulness(llm=eval_llm)],
        llm=eval_llm,
        raise_exceptions=False,
    )

    faith = float(results["faithfulness"])
    return {
        "synthesis_agent": {
            "faithfulness": round(faith, 4),
            "verdict": (
                "✅ Good — low hallucination"
                if faith > 0.80
                else "⚠️  Agent is hallucinating — review synthesis prompt"
            ),
        }
    }
