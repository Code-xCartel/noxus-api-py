from app.core.config import ApiConfig
from app.core.container import DepRegistry
from app.database.database import Database

common_deps = DepRegistry()

common_deps.register(ApiConfig, provider=ApiConfig)
common_deps.register(Database, provider=Database)
