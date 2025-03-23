from fastapi import FastAPI, Request
from app.core.config import ApiConfig
from app.core.container import DependencyContainer


class App(FastAPI):
    def __init__(
        self, *, config: ApiConfig = None, di: DependencyContainer = None, **kwargs
    ):
        self.config = config
        self.di = di
        super().__init__(**kwargs)

    def create_container_from_request(self, request: Request) -> DependencyContainer:
        pass  # TODO: implement dependency resolution
