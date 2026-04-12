from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.database import Base
import uuid


class Document(Base):
    """Document model for tracking uploaded PDFs."""

    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)

    # File details
    filename = Column(String, nullable=False)
    source_name = Column(String, nullable=False, index=True)

    # Processing details
    chunks_count = Column(Integer, default=0)
    file_size_bytes = Column(Integer, nullable=True)

    # Qdrant collection reference
    collection_name = Column(String, default="research_docs")

    # Timestamps
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    user = relationship("User", back_populates="documents")

    def __repr__(self):
        return f"<Document(id={self.id}, filename={self.filename}, chunks={self.chunks_count})>"
