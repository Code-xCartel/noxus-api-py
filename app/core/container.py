import inspect
from functools import lru_cache

from fastapi import Depends, Request
from starlette.websockets import WebSocket

from app.core.bound_repository import BoundRepository
from app.core.config import ApiConfig
from app.database.database import Database
from app.database.sql_client import SQLClient


class DependencyContainer:
    _instance = None

    def __new__(cls, api_config: ApiConfig = None, create_new: bool = False):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
            cls._instance._init(api_config)
        return cls._instance

    def _init(self, api_config: ApiConfig = None):
        self._db = Database(db_url=api_config.DB_PG_URL, echo=True)
        self._sql_client = SQLClient(self._db)
        self._repo = BoundRepository(self._sql_client)
        self._api_config = api_config

    def __init__(self, api_config: ApiConfig = None, create_new: bool = False):
        pass

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
def get_dependency_container(api_config: ApiConfig = None) -> DependencyContainer:
    return DependencyContainer(api_config=api_config)


def reqDep(cls, **kwargs):
    def resolve(
        request: Request = None,
        websocket: WebSocket = None,
    ):
        """
        Automatically resolves class dependencies.
        """
        container: DependencyContainer = DependencyContainer()

        if request and not hasattr(request.state, "dep_container"):
            request.state.dep_container = container

        if websocket and not hasattr(websocket.state, "dep_container"):
            websocket.state.dep_container = container

        init_params = inspect.signature(cls.__init__).parameters
        dependencies = {"request": request if request else websocket}

        for param_name, param in init_params.items():
            if param_name == "self":
                continue  # Ignore self parameter

            # Fetch from DependencyContainer using property name
            if hasattr(container, param_name):
                dependencies[param_name] = getattr(container, param_name)

        return cls(**dependencies)  # Instantiate class with resolved dependencies

    return Depends(resolve)
