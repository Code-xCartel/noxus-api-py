import base64
import hashlib
import hmac
import json
import time
from dataclasses import dataclass
from enum import Enum
from urllib.parse import quote

from fastapi import Request
from jose import JWTError, jwt
from starlette.authentication import AuthenticationError

from app.core.config import ApiConfig
from app.models.user import EmailIn


class AuthScheme(Enum):
    BEARER = "Bearer"


class AuthUtils:
    def __init__(self, api_config: ApiConfig):
        self.api_config = api_config

    @staticmethod
    def validate_request(request: Request = None, header: str = None):
        auth_header = header or request.headers.get("Authorization")
        if not auth_header:
            raise AuthenticationError("Authorization header required")

        parts = auth_header.split(" ")
        if len(parts) != 2:
            raise AuthenticationError(
                f"Invalid authorization header, got {len(parts)} parts, expected 2"
            )

        return parts

    @staticmethod
    def validate_scheme(scheme: str):
        if scheme not in [AuthScheme.BEARER.value]:
            raise AuthenticationError(f"Invalid authorization scheme, got {scheme}")

    def extract_payload_from_token(self, token: str):
        try:
            payload = jwt.decode(
                token,
                self.api_config.JWT_SECRET_KEY,
                algorithms=[self.api_config.JWT_ALGORITHM],
            )
            return UserRealm(
                username=payload["username"],
                email=payload["email"],
                nox_id=payload["nox_id"],
            )
        except JWTError as e:
            raise AuthenticationError(f"Invalid token, {str(e)}")

    @staticmethod
    def user_from_request(request: Request):
        if request.state.user:
            return request.state.user
        else:
            return None

    def generate_verification_link(self, request: EmailIn):
        secret = self.api_config.HMAC_SECRET_KEY.encode()
        payload = {
            "email": request.email,
            "timestamp": int(time.time()),
            "maxAgeMs": int(self.api_config.ACTIVATION_MAX_AGE),
        }
        json_payload = json.dumps(payload, separators=(",", ":")).encode()
        b64_payload = base64.urlsafe_b64encode(json_payload).decode()

        signature = hmac.new(secret, b64_payload.encode(), hashlib.sha256).hexdigest()

        return f"{self.api_config.NOXUS_URL}{self.api_config.NOXUS_ACTIVATION_ROUTE}?pkt={quote(b64_payload)}&sig={signature}"

    def extract_verification(self, pkt: str, sig: str):
        secret = self.api_config.HMAC_SECRET_KEY.encode()

        signature = hmac.new(secret, pkt.encode(), hashlib.sha256).hexdigest()
        if signature != sig:
            raise AuthenticationError()

        ext = base64.urlsafe_b64decode(pkt).decode()
        return ext


@dataclass(frozen=True)
class UserRealm:
    username: str = None
    email: str = None
    nox_id: str = None
