from sqlalchemy import Column, String, Integer, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.database import Base
import uuid


class User(Base):
    """User model for authentication and quota management."""

    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)

    # API access
    api_key = Column(String, unique=True, nullable=True, index=True)

    # Quota management
    quota_limit = Column(Integer, default=50)  # Requests per day
    quota_used = Column(Integer, default=0)
    quota_reset_at = Column(DateTime(timezone=True), nullable=True)

    # Account status
    is_active = Column(Boolean, default=True)
    is_premium = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    researches = relationship("Research", back_populates="user", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"
