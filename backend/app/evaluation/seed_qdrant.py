"""
Seed Qdrant with richer RAG knowledge base content.
Run once before evaluating: uv run python -m app.evaluation.seed_qdrant
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from app.tools.vector_store import vector_store
from app.services.embedding_service import embedding_service

print("Setting up local Qdrant collection...")
vector_store.ensure_collection()

# Rich, detailed chunks aligned with the 5 seed evaluation questions
sample_texts = [
    # --- What is RAG and how does it work? ---
    "Retrieval-Augmented Generation (RAG) is an AI framework that enhances large language models "
    "by grounding their responses in retrieved external knowledge. Given a user query, RAG first "
    "searches a vector database of documents using semantic similarity, retrieves the top-k most "
    "relevant chunks, and injects those chunks as context into the LLM prompt before generation. "
    "This two-stage process (retrieve then generate) allows the model to answer questions about "
    "knowledge not present in its training data without expensive retraining.",

    "The core components of a RAG system are: (1) a document store, where source texts are split "
    "into overlapping chunks (typically 256-512 tokens); (2) an embedding model that converts "
    "text to dense vector representations; (3) a vector database (e.g., Qdrant, Pinecone) that "
    "indexes the embeddings for fast approximate nearest-neighbour (ANN) search; and (4) a "
    "language model that generates answers conditioned on the retrieved passages.",

    # --- Methodology ---
    "The methodology of RAG systems involves four key steps: document ingestion, embedding "
    "indexing, retrieval, and generation. In the ingestion step, raw documents are parsed and "
    "chunked with configurable overlap (typically 10-20%) to preserve cross-boundary context. "
    "Each chunk is then embedded using a dense retrieval model such as text-embedding-004 or "
    "nomic-embed-text, producing 768 or 3072-dimensional vectors that capture semantic meaning.",

    "During retrieval, the user query is embedded with the same model and compared against stored "
    "vectors using cosine similarity. The top-k chunks (k=3 to 10) above a similarity threshold "
    "(0.5-0.7) are selected. These chunks are concatenated and inserted into the LLM prompt as "
    "context. The LLM (e.g., Gemini, LLaMA, GPT-4) is then instructed to answer using only "
    "the provided context, reducing reliance on potentially outdated parametric knowledge.",

    # --- Limitations ---
    "RAG systems have several well-documented limitations: (1) Context window constraints — "
    "most LLMs have token limits (4k-128k), and if retrieved chunks exceed this, information "
    "is lost. (2) Retrieval quality is bounded by the embedding model's semantic understanding — "
    "a poor embedding model returns irrelevant chunks, causing the LLM to hallucinate. "
    "(3) Chunking strategy matters — too small and chunks lose context; too large and they "
    "dilute relevance. (4) The system cannot reason across multiple documents simultaneously "
    "without multi-hop retrieval strategies.",

    "Additional limitations include latency overhead from the retrieval step, the cold-start "
    "problem (no documents ingested means no context retrieval), lack of real-time updates "
    "(vector stores must be re-indexed when source documents change), and difficulty handling "
    "queries that require mathematical reasoning or procedural knowledge not expressible as "
    "text passages. Faithfulness errors occur when the LLM adds information beyond the "
    "retrieved context, a key challenge measured by the faithfulness metric in RAGAS.",

    # --- RAG vs standard LLMs (results comparison) ---
    "In benchmark evaluations, RAG systems outperform vanilla LLMs on knowledge-intensive tasks. "
    "On the Natural Questions (NQ) benchmark, RAG achieves 44.5 EM (exact match) vs 29.8 EM "
    "for standard GPT-3, a 49% improvement. On TriviaQA, RAG reaches 56.8 vs 45.5 for the "
    "baseline. These improvements are attributed to grounding responses in retrieved evidence "
    "rather than relying solely on weights frozen at training time.",

    "RAG also significantly reduces hallucination rates. Studies show that RAG-augmented models "
    "produce factually grounded responses 72% of the time compared to 54% for unaugmented models "
    "on the same question set. However, when retrieval fails (no relevant chunks found), RAG "
    "models hallucinate at similar rates to their unaugmented counterparts, demonstrating that "
    "retrieval quality is the single biggest determinant of RAG faithfulness.",

    # --- Future improvements ---
    "Future research directions for RAG systems include: (1) Adaptive retrieval — dynamically "
    "deciding whether to retrieve at all based on query confidence. (2) Multi-hop reasoning — "
    "iteratively retrieving and synthesising across multiple documents to answer complex queries. "
    "(3) Hybrid sparse-dense retrieval — combining BM25 keyword search with dense vector search "
    "for improved recall on rare terms and proper nouns. (4) Real-time index updates with "
    "streaming ingestion pipelines that re-embed and re-index documents as they change.",

    "Additional recommended improvements for RAG pipelines include: self-RAG (the model learns "
    "to critique and re-retrieve when initial results are insufficient), cross-encoder re-ranking "
    "(a second-pass model that scores retrieved candidates for relevance before injection), "
    "and graph-RAG (using knowledge graphs to capture entity relationships beyond what "
    "vector similarity can express). Evaluation frameworks like RAGAS provide automated metrics "
    "(faithfulness, context recall, context precision) to measure and track these improvements.",
]

print(f"Embedding {len(sample_texts)} chunks...")
embeddings = embedding_service.embed_documents(sample_texts)
n = vector_store.upsert_documents(sample_texts, embeddings, 'rag_knowledge_base.pdf')
print(f"Uploaded {n} chunks.")

# Validate with a test query per seed question
test_queries = [
    "What is retrieval-augmented generation and how does it work?",
    "What are the limitations of RAG systems?",
    "What future improvements are recommended for RAG pipelines?",
]

print("\nQuery validation:")
for q in test_queries:
    q_vec = embedding_service.embed_query(q)
    docs = vector_store.query_documents(q_vec, limit=3, score_threshold=0.5)
    scores = [round(d['score'], 3) for d in docs]
    print(f"  '{q[:55]}...' -> {len(docs)} docs, scores: {scores}")

print("\nQdrant seeded and ready for evaluation.")
