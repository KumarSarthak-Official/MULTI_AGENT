from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from app.config import settings
from typing import List, Dict, Optional
import uuid


class VectorStore:
    """Qdrant vector store operations."""

    def __init__(self):
        self.client = QdrantClient(url=settings.QDRANT_URL)
        self.collection_name = "research_docs"

    def ensure_collection(self):
        """Create collection if it doesn't exist.

        Collection uses 768-dimensional vectors (nomic-embed-text) with cosine distance.
        """
        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]

        if self.collection_name not in collection_names:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=768, distance=Distance.COSINE),
            )
            print(f"Created collection: {self.collection_name}")
        else:
            print(f"Collection already exists: {self.collection_name}")

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
        if not texts or not embeddings:
            return 0

        if len(texts) != len(embeddings):
            raise ValueError("texts and embeddings must have same length")

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

        self.client.upsert(collection_name=self.collection_name, points=points)
        return len(points)


# Singleton instance
vector_store = VectorStore()
