from sqlalchemy import Column, String, Integer, Float, DateTime, Text, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.database import Base
import uuid


class Research(Base):
    """Research model for storing research requests and results."""

    __tablename__ = "researches"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)

    # Request details
    query = Column(Text, nullable=False)
    use_documents = Column(Boolean, default=True)

    # Status tracking
    status = Column(String, default="pending", index=True)  # pending, running, completed, failed

    # Results
    final_report = Column(Text, nullable=True)
    sources = Column(JSON, nullable=True)  # List of source dicts

    # Metrics
    duration_seconds = Column(Float, nullable=True)
    iteration_count = Column(Integer, default=0)
    critique_score = Column(Integer, nullable=True)

    # Error tracking
    error_message = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="researches")
    iterations = relationship("ResearchIteration", back_populates="research", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Research(id={self.id}, query={self.query[:50]}, status={self.status})>"


class ResearchIteration(Base):
    """Model for storing critique iterations during research refinement."""

    __tablename__ = "research_iterations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    research_id = Column(String, ForeignKey("researches.id"), nullable=False, index=True)

    # Iteration details
    iteration_number = Column(Integer, nullable=False)
    draft_report = Column(Text, nullable=False)

    # Critique results
    critique_score = Column(Integer, nullable=True)
    critique_feedback = Column(Text, nullable=True)

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    research = relationship("Research", back_populates="iterations")

    def __repr__(self):
        return f"<ResearchIteration(research_id={self.research_id}, iteration={self.iteration_number}, score={self.critique_score})>"
