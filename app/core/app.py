from fastapi import FastAPI, Request

from app.core.bound_repository import BoundRepository
from app.core.config import ApiConfig
from app.core.container import Container
from app.utils.auth_utils import UserRealm, AuthUtils


class App(FastAPI):
    di: Container
    config: ApiConfig

    def __init__(self, *, di: Container = None, config: ApiConfig = None, **kwargs):
        if di:
            self.di = di
        self.config = config or di.resolve(ApiConfig)
        super().__init__(**kwargs)

    def create_container_from_request(self, request: Request) -> Container:
        cont = self.di.clone(name="request")
        cont.register(Request, value=request)

        auth_utils: AuthUtils = cont.resolve(AuthUtils)
        cont.register(UserRealm, value=auth_utils.user_from_request(request))
        cont.register(BoundRepository, provider=BoundRepository)
        return cont
