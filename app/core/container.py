import inspect
from functools import lru_cache

from fastapi import Depends

from app.core.bound_repository import BoundRepository
from app.core.config import ApiConfig
from app.database.database import Database
from app.database.sql_client import SQLClient


class DependencyContainer:
    def __init__(self, api_config: ApiConfig):
        self._db = Database(db_url=api_config.DB_PG_URL, echo=True)
        self._sql_client = SQLClient(self._db)
        self._repo = BoundRepository(self._sql_client)
        self._api_config = api_config

    @property
    def db(self) -> Database:
        return self._db

    @property
    def sql_client(self) -> SQLClient:
        return self._sql_client

    @property
    def repo(self) -> BoundRepository:
        return self._repo

    @property
    def api_config(self) -> ApiConfig:
        return self._api_config


@lru_cache()
def get_dependency_container(api_config: ApiConfig) -> DependencyContainer:
    return DependencyContainer(api_config=api_config)


def reqDep(cls):
    def resolve(
        container: DependencyContainer = Depends(
            lambda: get_dependency_container(ApiConfig())
        ),
    ):
        """
        Automatically resolves class dependencies.
        """
        init_params = inspect.signature(cls.__init__).parameters
        dependencies = {}

        for param_name, param in init_params.items():
            if param_name == "self":
                continue  # Ignore self parameter

            # Fetch from DependencyContainer using property name
            if hasattr(container, param_name):
                dependencies[param_name] = getattr(container, param_name)

        return cls(**dependencies)  # Instantiate class with resolved dependencies

    return Depends(resolve)
