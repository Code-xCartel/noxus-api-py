from typing import Dict, Type, Union

from starlette.middleware.cors import CORSMiddleware

from app.core.config import ApiConfig

ALLOWED_METHODS = ["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS"]
ALLOWED_ORIGINS_FOR_LOCAL = ["*"]
ALLOWED_HEADERS = [
    "Authorization",
    "Cache-Control",
    "Content-Type",
    "DNT",
    "If-Modified-Since",
    "Keep-Alive",
    "User-Agent,X-Requested-With",
    "X-Token",
    "X-Proxy-User",
    "X-Session-Token",
    "X-Realm",
    "X-Real-IP",
    "X-Forwarded-For",
    "X-Email",
    "x-email",
]


def build_cors_config(config: ApiConfig) -> Dict[str, Union[Type[CORSMiddleware], str]]:
    cors_config = {
        "middleware_class": CORSMiddleware,
        "allow_origins": config.CORS_ALLOWED_HOST,
        "allow_methods": ALLOWED_METHODS,
        "allow_headers": ALLOWED_HEADERS,
    }

    if config.ALLOW_CORS_FOR_LOCAL or config.DEBUG:
        cors_config["allow_origins"] = ALLOWED_ORIGINS_FOR_LOCAL

    return cors_config
