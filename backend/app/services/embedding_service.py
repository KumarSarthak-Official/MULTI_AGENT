from langchain_ollama import OllamaEmbeddings
from app.config import settings
import os


class EmbeddingService:
    """Wrapper for Ollama Cloud embedding model."""

    def __init__(self):
        # Set API key as environment variable
        os.environ["OLLAMA_API_KEY"] = settings.OLLAMA_API_KEY

        self.embeddings = OllamaEmbeddings(
            model=settings.EMBED_MODEL,
            base_url=settings.OLLAMA_CLOUD_URL,
        )

    def embed_query(self, text: str) -> list[float]:
        """Generate embedding for a single query text.

        Args:
            text: Query text to embed

        Returns:
            List of floats representing the embedding vector (768-dim for nomic-embed-text)
        """
        return self.embeddings.embed_query(text)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple documents.

        Args:
            texts: List of document texts to embed

        Returns:
            List of embedding vectors
        """
        return self.embeddings.embed_documents(texts)


# Singleton instance
embedding_service = EmbeddingService()
