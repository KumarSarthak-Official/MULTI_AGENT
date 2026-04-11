from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.tools.vector_store import vector_store
from app.api.routes import health


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
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Multi-Agent Research Intelligence Platform API",
        "version": "0.1.0",
        "docs": "/docs",
    }
