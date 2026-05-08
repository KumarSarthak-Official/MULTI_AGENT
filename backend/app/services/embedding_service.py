from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.config import settings


class EmbeddingService:
    """Wrapper for Google Gemini embedding model (free tier).

    Uses Google's gemini-embedding-2-preview for high-quality embeddings.
    Ollama cloud models handle LLM tasks; Gemini handles embedding only.
    """

    def __init__(self):
        # Use separate instances with task_type for optimal retrieval quality
        self._query_embeddings = GoogleGenerativeAIEmbeddings(
            model=settings.GEMINI_EMBED_MODEL,
            google_api_key=settings.GOOGLE_API_KEY,
            task_type="RETRIEVAL_QUERY",
        )
        self._doc_embeddings = GoogleGenerativeAIEmbeddings(
            model=settings.GEMINI_EMBED_MODEL,
            google_api_key=settings.GOOGLE_API_KEY,
            task_type="RETRIEVAL_DOCUMENT",
        )

    def embed_query(self, text: str) -> list[float]:
        """Generate embedding for a single query text.

        Uses RETRIEVAL_QUERY task type for optimal search performance.

        Args:
            text: Query text to embed

        Returns:
            List of floats representing the embedding vector (768-dim default)
        """
        return self._query_embeddings.embed_query(text)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple documents.

        Uses RETRIEVAL_DOCUMENT task type for optimal indexing.
        Embeds each text individually because gemini-embedding-2-preview
        does not support true batch embedding via embed_documents.

        Args:
            texts: List of document texts to embed

        Returns:
            List of embedding vectors (same length as input texts)
        """
        if not texts:
            return []

        all_embeddings: list[list[float]] = []

        for i, text in enumerate(texts):
            embedding = self._doc_embeddings.embed_query(text)
            all_embeddings.append(embedding)
            if (i + 1) % 10 == 0:
                print(f"  Embedded {i + 1}/{len(texts)} chunks...")

        return all_embeddings


# Singleton instance
embedding_service = EmbeddingService()