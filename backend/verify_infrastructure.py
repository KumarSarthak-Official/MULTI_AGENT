#!/usr/bin/env python3
"""
Infrastructure Verification Script
Tests connectivity to PostgreSQL, Qdrant, and Redis
"""

import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'

from app.config import settings

def test_postgresql():
    """Test PostgreSQL connection."""
    try:
        from app.models import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("[OK] PostgreSQL: Connected successfully")
            return True
    except Exception as e:
        print(f"[FAIL] PostgreSQL: Connection failed - {e}")
        return False

def test_qdrant():
    """Test Qdrant connection."""
    try:
        from app.tools.vector_store import vector_store
        vector_store.ensure_collection()
        print("[OK] Qdrant: Connected successfully")
        print(f"     Collection: {vector_store.collection_name}")
        return True
    except Exception as e:
        print(f"[FAIL] Qdrant: Connection failed - {e}")
        return False

def test_redis():
    """Test Redis connection."""
    try:
        from app.services.cache_service import cache_service
        if not cache_service.enabled:
            print("[WARN] Redis: Not configured (caching disabled)")
            return False

        # Test set/get
        test_key = "test:connectivity"
        cache_service.set(test_key, "test_value", ttl=10)
        value = cache_service.get(test_key)
        cache_service.delete(test_key)

        if value == "test_value":
            print("[OK] Redis: Connected successfully")
            return True
        else:
            print("[FAIL] Redis: Connection test failed")
            return False
    except Exception as e:
        print(f"[FAIL] Redis: Connection failed - {e}")
        return False

def main():
    print("=" * 60)
    print("Infrastructure Connectivity Test")
    print("=" * 60)
    print()

    results = {
        "PostgreSQL": test_postgresql(),
        "Qdrant": test_qdrant(),
        "Redis": test_redis(),
    }

    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)

    passed = sum(results.values())
    total = len(results)

    for service, status in results.items():
        status_icon = "[OK]" if status else "[FAIL]"
        print(f"{status_icon} {service}")

    print()
    print(f"Result: {passed}/{total} services connected")

    if passed == total:
        print()
        print("SUCCESS: All services are ready!")
        print("You can now start the application.")
        return 0
    else:
        print()
        print("WARNING: Some services are not connected.")
        print("Please check INFRASTRUCTURE_SETUP.md for setup instructions.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
