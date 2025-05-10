from app.core.abstrcations import resolve_abstractions
from app.core.config import ApiConfig
from app.core.container import DepRegistry
from app.database.database import Database
from app.services.caching.abstract_caching_service import AbstractCachingService

common_deps = DepRegistry()

common_deps.register(ApiConfig, provider=ApiConfig)
common_deps.register(Database, provider=Database)
common_deps.register(
    AbstractCachingService,
    patch_provider=resolve_abstractions,
    patch_params={"abstraction_name": "CACHING_SERVICE"},
)
