import re
from functools import cached_property
from typing import Any, Optional, Type

from starlette.config import Config

_config = Config(".env")


class ConfigVar:
    VALUES_ATTR_NAME = "_config_values"

    def __init__(self, key: str, **kwargs: Any) -> None:
        self.key = key
        self.definition = kwargs
        self.init_value = _config(self.key, **self.definition)

    def __get__(self, instance: Optional[object], owner: Type[object]) -> Any:
        if instance is None:
            return self

        if not hasattr(instance, self.VALUES_ATTR_NAME):
            setattr(instance, self.VALUES_ATTR_NAME, {})

        config_values = getattr(instance, self.VALUES_ATTR_NAME)
        if self.key not in config_values:
            config_values[self.key] = self.init_value
        return config_values[self.key]

    def __set__(self, instance: Optional[object], value: Any):
        pass  # TODO: implement


class ApiConfig:
    API_VERSION = ConfigVar("API_VERSION", default="1")
    API_PREFIX = ConfigVar("API_PREFIX", default=f"/api/v{API_VERSION.init_value}")
    DB_PG_URL = ConfigVar(
        "DB_PG_URL", default="postgresql://postgres:postgres@localhost/postgres"
    )
    JWT_SECRET_KEY = ConfigVar("JWT_SECRET_KEY", default="secret")
    JWT_ALGORITHM = ConfigVar("ALGORITHM", default="HS256")
    JWT_EXPIRATION_DELTA = ConfigVar("JWT_EXPIRATION_DELTA", default=7)
    CORS_ALLOWED_HOST = ConfigVar("CORS_ALLOWED_HOST", default="*")
    ALLOW_CORS_FOR_LOCAL = ConfigVar("ALLOW_CORS_FOR_LOCAL", default=True)
    DEBUG = ConfigVar("DEBUG", default=True)

    @cached_property
    def SKIP_AUTH_ROUTES(self):
        return (
            re.compile(r"^/favicon.ico"),
            re.compile(rf"^{self.API_PREFIX}/docs$"),
            re.compile(rf"^{self.API_PREFIX}/redoc$"),
            re.compile(rf"^{self.API_PREFIX}/openapi.json$"),
            re.compile(rf"^{self.API_PREFIX}/auth/register$"),
            re.compile(rf"^{self.API_PREFIX}/auth/login$"),
        )

    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
            "simple": {"format": "%(levelname)s - %(message)s"},
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "detailed",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.FileHandler",
                "level": "DEBUG",
                "formatter": "detailed",
                "filename": "app.log",
                "mode": "a",
            },
        },
        "loggers": {
            "": {  # Root logger
                "level": "DEBUG",
                "handlers": ["console", "file"],
            },
        },
    }
