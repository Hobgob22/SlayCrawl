from redis import asyncio as aioredis
from typing import Optional, Any, Dict
import json
import os
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

class RedisCache:
    """Redis cache manager for the scraping service."""
    
    def __init__(self, redis_url: Optional[str] = None):
        """Initialize Redis connection."""
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://redis:6379")
        self.redis = aioredis.from_url(
            self.redis_url,
            encoding="utf-8",
            decode_responses=True
        )
        self.default_expiry = int(os.getenv("CACHE_EXPIRY", 3600))  # 1 hour default
    
    async def get_cached_data(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached data for a given key.
        
        Args:
            key: Cache key to look up
            
        Returns:
            Optional[Dict]: Cached data if found, None otherwise
        """
        try:
            data = await self.redis.get(f"scrape:{key}")
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Redis get error: {str(e)}")
            return None
    
    async def cache_data(self, key: str, data: Dict[str, Any], expiry: Optional[int] = None) -> bool:
        """
        Cache data with the given key.
        
        Args:
            key: Cache key
            data: Data to cache
            expiry: Optional custom expiry time in seconds
            
        Returns:
            bool: True if caching was successful
        """
        try:
            await self.redis.setex(
                f"scrape:{key}",
                expiry or self.default_expiry,
                json.dumps(data)
            )
            return True
        except Exception as e:
            logger.error(f"Redis set error: {str(e)}")
            return False
    
    async def invalidate(self, key: str) -> bool:
        """
        Remove data from cache.
        
        Args:
            key: Cache key to invalidate
            
        Returns:
            bool: True if invalidation was successful
        """
        try:
            await self.redis.delete(f"scrape:{key}")
            return True
        except Exception as e:
            logger.error(f"Redis delete error: {str(e)}")
            return False
    
    async def get_or_set(
        self,
        key: str,
        data_generator: callable,
        expiry: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get data from cache or generate and cache it if not found.
        
        Args:
            key: Cache key
            data_generator: Async function to generate data if not in cache
            expiry: Optional custom expiry time in seconds
            
        Returns:
            Dict: The cached or newly generated data
        """
        cached_data = await self.get_cached_data(key)
        if cached_data:
            return cached_data
        
        new_data = await data_generator()
        await self.cache_data(key, new_data, expiry)
        return new_data
    
    async def close(self):
        """Close the Redis connection."""
        await self.redis.close()

# Create global cache instance
cache = RedisCache() 