import re
from datetime import timedelta
from functools import cached_property

from starlette.config import Config

config = Config(".env")


class ApiConfig:
    API_VERSION: str = config("API_VERSION", default="1")
    API_PREFIX: str = config("API_PREFIX", default=f"/api/v{API_VERSION}")
    DB_PG_URL = config(
        "DB_PG_URL", default="postgresql://postgres:postgres@localhost/postgres"
    )
    JWT_SECRET_KEY: str = config("JWT_SECRET_KEY", default="secret")
    JWT_ALGORITHM: str = config("ALGORITHM", default="HS256")
    JWT_EXPIRATION_DELTA = config("JWT_EXPIRATION_DELTA", default=7)
    CORS_ALLOWED_HOST = config("CORS_ALLOWED_HOST", default="*")
    ALLOW_CORS_FOR_LOCAL: bool = config("ALLOW_CORS_FOR_LOCAL", default=True)
    DEBUG: bool = config("DEBUG", default=True)

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
