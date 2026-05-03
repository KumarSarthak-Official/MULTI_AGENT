from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from app.models.database import SessionLocal
from app.models.user import User
from sqlalchemy.orm import Session

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def _get_or_create_default_user(db: Session) -> User:
    """Get or create the default development user."""
    user = db.query(User).filter(User.email == "default@example.com").first()
    if not user:
        user = User(email="default@example.com", password_hash="placeholder")
        db.add(user)
        db.commit()
    # Eagerly load the id so it's available after session closes
    db.refresh(user)
    return user


def get_current_user(api_key: str = Security(api_key_header)) -> User:
    """Authenticate user via API key header.

    Falls back to a default dev user if no key is provided.
    In production, remove the fallback and enforce key-only auth.
    """
    db = SessionLocal()
    try:
        if not api_key:
            # Development fallback: auto-create default user
            user = _get_or_create_default_user(db)
        else:
            user = db.query(User).filter(User.api_key == api_key).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid API Key",
                )
            db.refresh(user)

        # Expunge the user from the session so it stays usable after close
        db.expunge(user)
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication error: {str(e)}",
        )
    finally:
        db.close()
