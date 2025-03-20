from fastapi import FastAPI
from app.core.config import ApiConfig
from app.core.container import DependencyContainer
from app.database.database import Database


class App(FastAPI):
    def __init__(
        self, *, config: ApiConfig = None, di: DependencyContainer = None, **kwargs
    ):
        self.config = config
        self.di = di
        super().__init__(**kwargs)
