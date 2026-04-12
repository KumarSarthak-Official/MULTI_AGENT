# Database Setup Script
# Run this to create all tables in your local PostgreSQL

from app.models import Base, engine

def create_tables():
    """Create all database tables."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ All tables created successfully!")

if __name__ == "__main__":
    create_tables()
