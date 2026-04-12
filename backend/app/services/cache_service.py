import redis
from app.config import settings
from typing import Optional
import json


class CacheService:
    """Redis caching service for LLM responses and search results."""

    def __init__(self):
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=5,
            )
            # Test connection
            self.redis_client.ping()
            self.enabled = True
        except Exception as e:
            print(f"Redis connection failed: {e}")
            print("Caching disabled - continuing without Redis")
            self.enabled = False

    def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        if not self.enabled:
            return None

        try:
            return self.redis_client.get(key)
        except Exception as e:
            print(f"Cache get error: {e}")
            return None

    def set(self, key: str, value: str, ttl: int = 3600) -> bool:
        """Set value in cache with TTL (default 1 hour)."""
        if not self.enabled:
            return False

        try:
            self.redis_client.setex(key, ttl, value)
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False

    def get_json(self, key: str) -> Optional[dict]:
        """Get JSON value from cache."""
        value = self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return None
        return None

    def set_json(self, key: str, value: dict, ttl: int = 3600) -> bool:
        """Set JSON value in cache."""
        try:
            json_str = json.dumps(value)
            return self.set(key, json_str, ttl)
        except Exception as e:
            print(f"Cache set_json error: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self.enabled:
            return False

        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False

    def clear_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern."""
        if not self.enabled:
            return 0

        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            print(f"Cache clear_pattern error: {e}")
            return 0


# Singleton instance
cache_service = CacheService()
