from fastapi import APIRouter
from datetime import datetime, timezone
from app.models.database import engine
from sqlalchemy import text
from app.services.cache_service import cache_service

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint.

    Returns:
        dict: Health status and timestamp
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "multi-agent-research-platform",
    }

@router.get("/health/ready")
async def readiness_check():
    """Readiness check endpoint that verifies dependencies."""
    status = "healthy"
    dependencies = {
        "database": "unknown",
        "redis": "unknown"
    }
    
    # Check DB
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            dependencies["database"] = "healthy"
    except Exception as e:
        dependencies["database"] = f"unhealthy: {str(e)}"
        status = "unhealthy"

    # Check Redis
    if cache_service.enabled:
        try:
            cache_service.redis_client.ping()
            dependencies["redis"] = "healthy"
        except Exception as e:
            dependencies["redis"] = f"unhealthy: {str(e)}"
            status = "unhealthy"
    else:
        dependencies["redis"] = "disabled"

    return {
        "status": status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dependencies": dependencies,
    }
