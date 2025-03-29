from app.api.routes.api import router
from app.core.app import App
from app.core.config import ApiConfig
from app.core.container import Container
from app.dependencies import common_deps
from app.middleware.authorization import (
    AuthorizationMiddleware,
    WSAuthorizationMiddleware,
)
from app.utils.auth_utils import AuthUtils
from app.utils.cors import build_cors_config


def create_app(*, di: Container = None) -> App:
    if di is None:
        di = Container(dependencies=common_deps)

    config: ApiConfig = di.resolve(ApiConfig)

    _app = App(
        di=di,
        config=config,
        title="Noxus API",
        description="The official Noxus API. Made with &#9829;.",
        openapi_url=f"{config.API_PREFIX}/openapi.json",
        docs_url=f"{config.API_PREFIX}/docs",
        redoc_url=f"{config.API_PREFIX}/redoc",
        debug=config.DEBUG,
    )
    _app.add_middleware(WSAuthorizationMiddleware, auth_utils=di.resolve(AuthUtils))
    _app.add_middleware(
        AuthorizationMiddleware,
        config=config,
        auth_utils=di.resolve(AuthUtils),
    )
    _app.add_middleware(**build_cors_config(config))
    _app.include_router(router, prefix=config.API_PREFIX)

    return _app
