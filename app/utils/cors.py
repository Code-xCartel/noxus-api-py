from starlette.middleware.cors import CORSMiddleware

from app.core.config import ApiConfig
from typing import Dict, Union, Type

ALLOWED_METHODS = ["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS"]
ALLOWED_ORIGINS_FOR_LOCAL = ["*"]
ALLOWED_ORIGIN_REGEX = "https://.*\.{host}"
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
        "allow_origin_regex": ALLOWED_ORIGIN_REGEX.format(
            host=config.CORS_ALLOWED_HOST.replace(".", "\\.")
        ),
        "allow_methods": ALLOWED_METHODS,
        "allow_headers": ALLOWED_HEADERS,
    }

    if config.ALLOW_CORS_FOR_LOCAL or config.DEBUG:
        cors_config["allow_origins"] = ALLOWED_ORIGINS_FOR_LOCAL
        del cors_config["allow_origin_regex"]

    return cors_config
