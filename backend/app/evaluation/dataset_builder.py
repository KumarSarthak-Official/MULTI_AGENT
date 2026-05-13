"""
Evaluation Dataset Builder
============================
Two modes:
  A. Synthetic  – run the production pipeline against hand-picked seed questions.
                  Best for fresh evaluation when you don't have stored history.
  B. Auto-gen   – RAGAS TestsetGenerator creates Q&A pairs directly from a PDF.
                  Run once per new document type to grow a regression suite.

The dataset schema expected by RAGAS v0.4+:
  user_input        – the question posed to the system
  response          – the answer produced by the agent pipeline
  retrieved_contexts – list of context strings passed to the LLM
  reference          – (optional) ground-truth answer for answer_correctness
"""

import asyncio
from datasets import Dataset
from app.agents.graph import research_graph
from app.tools.vector_store import vector_store
from app.services.embedding_service import embedding_service


# --------------------------------------------------------------------------
# Seed questions – representative of what your users actually ask.
# Tune these to reflect your domain (research papers, tech docs, etc.).
# --------------------------------------------------------------------------
SEED_QUESTIONS = [
    "What is retrieval-augmented generation and how does it work?",
    "What is the methodology used in RAG systems?",
    "What are the limitations of RAG systems?",
    "How does RAG compare to standard language models in terms of accuracy?",
    "What future improvements are recommended for RAG pipelines?",
]


# --------------------------------------------------------------------------
# Helper: retrieve contexts from Qdrant using the production retrieval path
# --------------------------------------------------------------------------
def _retrieve_contexts(query: str, top_k: int = 5) -> list[str]:
    """
    Mirrors what the RAG agent does: embed → query Qdrant → return text strings.
    Returns an empty list gracefully if Qdrant is unavailable or empty.
    """
    try:
        query_vector = embedding_service.embed_query(query)
        docs = vector_store.query_documents(
            query_vector=query_vector,
            limit=top_k,
            score_threshold=0.4,  # slightly lower than prod to capture more context
        )
        return [d["text"] for d in docs if d.get("text")]
    except Exception as e:
        print(f"  ⚠️  Context retrieval failed for '{query}': {e}")
        return []


# --------------------------------------------------------------------------
# OPTION A: Synthetic dataset — runs the full multi-agent pipeline
# --------------------------------------------------------------------------
async def build_synthetic_dataset(
    questions: list[str] | None = None,
    use_documents: bool = True,
) -> Dataset:
    """
    Build an EvaluationDataset by running the production pipeline for each
    question and capturing the (question, answer, retrieved_contexts) triple.

    Args:
        questions:     Questions to evaluate. Defaults to SEED_QUESTIONS.
        use_documents: Whether to enable the RAG agent (set False to test
                       web-search-only performance).

    Returns:
        HuggingFace Dataset ready for RAGAS evaluate().
    """
    questions = questions or SEED_QUESTIONS
    samples: list[dict] = []

    for i, q in enumerate(questions, 1):
        print(f"  [{i}/{len(questions)}] Running pipeline for: {q!r}")
        try:
            # Run the LangGraph pipeline synchronously inside an async context
            state = research_graph.invoke(
                {
                    "query": q,
                    "use_documents": use_documents,
                    "messages": [],
                    "search_results": [],
                    "rag_context": [],
                    "sources": [],
                    "agent_logs": [],
                    "iteration_count": 0,
                }
            )

            response = state.get("final_report") or state.get("draft_report") or ""

            # ── Collect ALL context the synthesis agent actually used ──────
            # 1. RAG chunks from Qdrant
            rag_contexts: list[str] = []
            if state.get("rag_context"):
                rag_contexts = [
                    c.get("text", "")
                    for c in state["rag_context"]
                    if c.get("text")
                ]

            # Fallback: re-query Qdrant directly if pipeline state is empty
            if not rag_contexts:
                rag_contexts = _retrieve_contexts(q)

            # 2. Web search snippets — these are ALSO given to the synthesis
            #    agent, so RAGAS must see them to correctly judge faithfulness.
            web_contexts: list[str] = []
            if state.get("search_results"):
                web_contexts = [
                    f"[Web] {r.get('title', '')}: {r.get('snippet', '')}"
                    for r in state["search_results"]
                    if r.get("snippet")
                ]

            # Combine: RAG first (primary), web second (supplementary)
            all_contexts = rag_contexts + web_contexts
            if not all_contexts:
                all_contexts = ["No context retrieved"]

            samples.append(
                {
                    "user_input": q,
                    "response": response,
                    "retrieved_contexts": all_contexts,
                    "reference": "",  # fill in ground-truth later if available
                }
            )
        except Exception as e:
            print(f"  ❌ Pipeline failed for '{q}': {e}")
            samples.append(
                {
                    "user_input": q,
                    "response": f"[ERROR] {e}",
                    "retrieved_contexts": [],
                    "reference": "",
                }
            )

    return Dataset.from_list(samples)


# --------------------------------------------------------------------------
# OPTION B: Auto-generate a test set from a PDF using RAGAS TestsetGenerator
# --------------------------------------------------------------------------
async def generate_testset_from_pdf(
    pdf_path: str,
    test_size: int = 25,
) -> Dataset:
    """
    Use RAGAS TestsetGenerator to synthesise Q&A pairs directly from a PDF.
    Run once per document type to build a reusable regression suite.

    Args:
        pdf_path:  Absolute or relative path to a PDF file.
        test_size: Number of test cases to generate.

    Returns:
        HuggingFace Dataset with user_input, reference columns.
    """
    from ragas.testset import TestsetGenerator
    from langchain_community.document_loaders import PyPDFLoader
    from app.evaluation.config import eval_llm, eval_embeddings

    print(f"📄 Loading PDF: {pdf_path}")
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    if not documents:
        raise ValueError(f"No pages loaded from {pdf_path}")

    print(f"🤖 Generating {test_size} test cases …")
    generator = TestsetGenerator(
        llm=eval_llm,
        embedding_model=eval_embeddings,
    )
    testset = generator.generate_with_langchain_docs(
        documents,
        testset_size=test_size,
    )

    df = testset.to_pandas()
    print(f"✅ Generated {len(df)} test cases from {pdf_path}")
    print(df[["user_input", "reference"]].head())

    return Dataset.from_pandas(df)
