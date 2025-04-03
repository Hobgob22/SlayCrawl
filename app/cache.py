from redis import asyncio as aioredis
import json
from typing import Optional, Any
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

class Cache:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis = aioredis.from_url(redis_url, encoding="utf-8", decode_responses=True)
        self.default_ttl = timedelta(hours=24)

    async def get(self, key: str) -> Optional[Any]:
        try:
            data = await self.redis.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Error getting key {key} from cache: {str(e)}")
            return None

    async def set(self, key: str, value: Any, ttl: Optional[timedelta] = None) -> bool:
        try:
            ttl = ttl or self.default_ttl
            serialized = json.dumps(value)
            await self.redis.set(key, serialized, ex=int(ttl.total_seconds()))
            return True
        except Exception as e:
            logger.error(f"Error setting key {key} in cache: {str(e)}")
            return False

    async def delete(self, key: str) -> bool:
        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"Error deleting key {key} from cache: {str(e)}")
            return False

    async def exists(self, key: str) -> bool:
        try:
            return await self.redis.exists(key) > 0
        except Exception as e:
            logger.error(f"Error checking existence of key {key} in cache: {str(e)}")
            return False

    def get_key(self, url: str, params: Optional[dict] = None) -> str:
        """Generate a cache key from URL and optional parameters"""
        key = f"slaycrawl:{url}"
        if params:
            param_str = json.dumps(params, sort_keys=True)
            key += f":{param_str}"
        return key

    async def close(self):
        await self.redis.close() 