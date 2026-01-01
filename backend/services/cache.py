"""
Redis cache service for calorie lookup caching.
"""
import json
import redis
from typing import Optional, Any
from functools import wraps
from settings import settings


class RedisCache:
    """Redis-backed cache for calorie computations and lookups."""
    
    def __init__(self, url: str):
        self.client = None
        try:
            self.client = redis.from_url(url, decode_responses=True)
            # Test connection
            self.client.ping()
            print("✓ Redis connection established")
        except Exception as e:
            print(f"⚠ Redis not available: {e}")
            self.client = None
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value by key."""
        if not self.client:
            return None
        try:
            value = self.client.get(key)
            return json.loads(value) if value else None
        except Exception:
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        """Set cached value with TTL (default 1 hour)."""
        if not self.client:
            return
        try:
            self.client.setex(key, ttl, json.dumps(value))
        except Exception:
            pass
    
    def delete(self, key: str):
        """Delete cached value."""
        if not self.client:
            return
        try:
            self.client.delete(key)
        except Exception:
            pass
    
    def clear_pattern(self, pattern: str):
        """Clear all keys matching pattern."""
        if not self.client:
            return
        try:
            keys = self.client.keys(pattern)
            if keys:
                self.client.delete(*keys)
        except Exception:
            pass


# Global cache instance
cache = RedisCache(settings.REDIS_URL)


def cached(ttl: int = 3600, key_prefix: str = ""):
    """
    Decorator for caching function results in Redis.
    
    Args:
        ttl: Time to live in seconds (default 1 hour)
        key_prefix: Prefix for cache key
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Build cache key
            key_parts = [key_prefix or func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = ":".join(key_parts)
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Compute and cache
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator
