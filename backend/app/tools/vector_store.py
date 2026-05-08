from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from app.config import settings
from typing import List, Dict, Optional
import uuid
import time


# Batch size for upserts — keeps individual payloads small
_UPSERT_BATCH_SIZE = 50
# Retry settings for transient network errors
_MAX_RETRIES = 3
_RETRY_BACKOFF = 2.0  # seconds; doubles each attempt


class VectorStore:
    """Qdrant vector store operations with support for both local and cloud."""

    def __init__(self):
        self.connected = False
        # Support both local Qdrant and Qdrant Cloud
        if settings.QDRANT_API_KEY:
            # Qdrant Cloud with API key authentication
            self.client = QdrantClient(
                url=settings.QDRANT_URL,
                api_key=settings.QDRANT_API_KEY,
                timeout=30,
            )
        else:
            # Local Qdrant without authentication
            self.client = QdrantClient(url=settings.QDRANT_URL, timeout=30)

        self.collection_name = "research_docs"

    def _upsert_with_retry(self, points: List[PointStruct]) -> None:
        """Upsert a batch of points with retry/backoff on transient errors."""
        delay = _RETRY_BACKOFF
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                self.client.upsert(
                    collection_name=self.collection_name, points=points
                )
                return
            except Exception as e:
                if attempt == _MAX_RETRIES:
                    raise
                print(
                    f"  Qdrant upsert attempt {attempt} failed ({e}), "
                    f"retrying in {delay:.0f}s..."
                )
                time.sleep(delay)
                delay *= 2

    def ensure_collection(self):
        """Create collection if it doesn't exist.

        Dynamically checks embedding dimension to ensure compatibility.
        """
        from app.services.embedding_service import embedding_service
        
        try:
            sample = embedding_service.embed_query("test dimension")
            current_dim = len(sample)
            print(f"Current embedding dimension: {current_dim}")
        except Exception as e:
            print(f"Failed to get embedding dimension: {e}")
            current_dim = 768  # Fallback

        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]

        if self.collection_name in collection_names:
            collection_info = self.client.get_collection(self.collection_name)
            # Access size appropriately based on the structure (params or vectors directly)
            if hasattr(collection_info.config.params, 'vectors') and hasattr(collection_info.config.params.vectors, 'size'):
                existing_dim = collection_info.config.params.vectors.size
            else:
                existing_dim = collection_info.config.params.vectors.size if hasattr(collection_info.config.params, 'vectors') else collection_info.config.params.size
                
            if existing_dim != current_dim:
                print(f"Dimension mismatch (expected {current_dim}, found {existing_dim}). Recreating collection...")
                self.client.delete_collection(self.collection_name)
                collection_names.remove(self.collection_name)

        if self.collection_name not in collection_names:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=current_dim, distance=Distance.COSINE),
            )
            print(f"Created collection: {self.collection_name} with dim {current_dim}")
        else:
            print(f"Collection already exists: {self.collection_name} with dim {current_dim}")

        self.connected = True

    def query_documents(
        self,
        query_vector: List[float],
        limit: int = 10,
        score_threshold: float = 0.5,
    ) -> List[Dict]:
        """Query documents from Qdrant using vector similarity.

        Args:
            query_vector: Embedding vector for the query
            limit: Maximum number of results to return
            score_threshold: Minimum similarity score (0-1)

        Returns:
            List of dicts with keys: text, source, score, page, chunk_index
        """
        try:
            # Check if collection exists and has documents
            collection_info = self.client.get_collection(self.collection_name)
            if collection_info.points_count == 0:
                print(f"Collection '{self.collection_name}' is empty")
                return []

            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold,
            )

            documents = []
            for result in results:
                documents.append({
                    "text": result.payload.get("text", ""),
                    "source": result.payload.get("source", ""),
                    "score": result.score,
                    "page": result.payload.get("page", 0),
                    "chunk_index": result.payload.get("chunk_index", 0),
                })

            return documents

        except Exception as e:
            print(f"Error querying documents: {e}")
            return []

    def upsert_documents(
        self,
        texts: List[str],
        embeddings: List[List[float]],
        source: str,
        metadata: Optional[List[Dict]] = None,
    ) -> int:
        """Insert or update documents in Qdrant.

        Args:
            texts: List of text chunks
            embeddings: List of embedding vectors
            source: Source name for all chunks
            metadata: Optional list of metadata dicts (page, chunk_index, etc.)

        Returns:
            Number of chunks inserted
        """
        if not self.connected:
            raise ConnectionError(
                "Qdrant is not connected. Check your QDRANT_URL and QDRANT_API_KEY."
            )

        if not texts or not embeddings:
            return 0

        if len(texts) != len(embeddings):
            raise ValueError(
                f"texts and embeddings must have same length "
                f"(got {len(texts)} texts, {len(embeddings)} embeddings)"
            )

        points = []
        for i, (text, embedding) in enumerate(zip(texts, embeddings)):
            payload = {
                "text": text,
                "source": source,
                "page": metadata[i].get("page", i) if metadata else i,
                "chunk_index": metadata[i].get("chunk_index", i) if metadata else i,
            }

            points.append(
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=embedding,
                    payload=payload,
                )
            )

        # Upsert in batches to avoid large payloads and handle network drops
        total = len(points)
        for i in range(0, total, _UPSERT_BATCH_SIZE):
            batch = points[i : i + _UPSERT_BATCH_SIZE]
            print(f"  Upserting batch {i // _UPSERT_BATCH_SIZE + 1}/"
                  f"{(total + _UPSERT_BATCH_SIZE - 1) // _UPSERT_BATCH_SIZE} "
                  f"({len(batch)} points)...")
            self._upsert_with_retry(batch)

        return total


# Singleton instance
vector_store = VectorStore()
