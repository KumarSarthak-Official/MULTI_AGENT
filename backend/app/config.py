from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/research_db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # Qdrant
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str = ""  # Optional for local, required for Qdrant Cloud

    # Ollama Cloud (for LLM / research agents)
    OLLAMA_CLOUD_URL: str = "https://api.ollama.com"
    OLLAMA_API_KEY: str

    # Google Gemini (for RAG embeddings - free tier)
    GOOGLE_API_KEY: str = ""
    GEMINI_EMBED_MODEL: str = "gemini-embedding-2-preview"

    # Models (Ollama cloud model for LLM tasks)
    LLM_MODEL: str = "deepseek-v4-pro:cloud"

    # API
    CORS_ORIGINS: str = "http://localhost:3000"

    # NVIDIA NIM (for RAGAS evaluation)
    NVIDIA_API_KEY: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
