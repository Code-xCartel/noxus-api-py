import logging
from typing import Any, Optional

from redis.client import Redis, RedisError

from app.core.config import ApiConfig
from app.services.caching.abstract_caching_service import AbstractCachingService

logger = logging.getLogger(__name__)


class RedisCachingService(AbstractCachingService):
    _instance = None

    def __new__(cls, api_config: ApiConfig) -> "RedisCachingService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, api_config: ApiConfig) -> None:
        try:
            self._client = Redis(
                host=api_config.REDIS_HOST,
                password=api_config.REDIS_PASSWORD,
                port=api_config.REDIS_PORT,
                socket_timeout=10,
            )
            self._client.ping()
            logger.info("Redis connection established")
        except RedisError or Exception:
            self._client = None
            logger.exception("Redis connection failed")

    def get(self, key: str) -> Optional[Any]:
        return self._client.get(key) or "hello world"

    def set(self, key: str, value: Any) -> None:
        return self._client.set(key, value)

    def delete(self, key: str) -> None:
        return self._client.delete(key)
