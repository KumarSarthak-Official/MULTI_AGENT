from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/research_db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # Qdrant
    QDRANT_URL: str = "http://localhost:6333"

    # Ollama Cloud
    OLLAMA_CLOUD_URL: str = "https://api.ollama.com"
    OLLAMA_API_KEY: str

    # Models
    LLM_MODEL: str = "qwen2.5"
    EMBED_MODEL: str = "nomic-embed-text"

    # API
    CORS_ORIGINS: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
