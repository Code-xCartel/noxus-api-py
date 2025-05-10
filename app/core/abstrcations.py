from enum import Enum

from app.core.config import ApiConfig
from app.services.caching.redis_caching_service import RedisCachingService


class CachingProviders(Enum):
    REDIS = "redis"


abstraction_mapping = {
    "CACHING_SERVICE": {CachingProviders.REDIS.value: RedisCachingService}
}


def resolve_abstractions(api_config: ApiConfig, **kwargs):
    abstraction_name = kwargs.get("abstraction_name", "")
    requirement = getattr(api_config, abstraction_name, None)
    implementation = abstraction_mapping.get(abstraction_name, {}).get(
        requirement, None
    )
    return implementation
