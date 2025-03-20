from app.api.routes.api import router
from app.core.app import App
from app.core.config import ApiConfig
from app.core.container import DependencyContainer, get_dependency_container
from app.middleware.authorization import AuthorizationMiddleware
from app.utils.cors import build_cors_config


def create_app():
    config: ApiConfig = ApiConfig()
    di: DependencyContainer = get_dependency_container(api_config=config)
    _app = App(
        config=config,
        di=di,
        title="Noxus API",
        description="The official Noxus API. Made with &#9829;.",
        openapi_url=f"{config.API_PREFIX}/openapi.json",
        docs_url=f"{config.API_PREFIX}/docs",
        redoc_url=f"{config.API_PREFIX}/redoc",
        debug=config.DEBUG,
    )
    _app.add_middleware(AuthorizationMiddleware, _app=_app)
    _app.add_middleware(**build_cors_config(config))
    _app.include_router(router, prefix=config.API_PREFIX)
    return _app
