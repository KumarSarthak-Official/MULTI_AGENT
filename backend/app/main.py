from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.tools.vector_store import vector_store
from app.api.routes import health, research, documents
from app.api.eval_router import router as eval_router
from app.limiter import limiter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup: Ensure Qdrant collection exists
    print("Starting up: Ensuring Qdrant collection exists...")
    try:
        vector_store.ensure_collection()
        print("Qdrant collection ready")
    except Exception as e:
        print(f"Warning: Could not connect to Qdrant: {e}")
        print("RAG functionality will be limited until Qdrant is available")

    yield

    # Shutdown
    print("Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Multi-Agent Research Intelligence Platform",
    description="AI-powered research system with 4 specialized agents",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
origins = settings.CORS_ORIGINS.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept", "Cache-Control", "X-Accel-Buffering"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(research.router, prefix="/api/v1", tags=["research"])
app.include_router(documents.router, prefix="/api/v1", tags=["documents"])
app.include_router(eval_router, prefix="/api/v1", tags=["evaluation"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Multi-Agent Research Intelligence Platform API",
        "version": "0.1.0",
        "docs": "/docs",
    }
