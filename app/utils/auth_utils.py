from dataclasses import dataclass
from enum import Enum

from fastapi import Request
from jose import JWTError, jwt
from starlette.authentication import AuthenticationError

from app.core.config import ApiConfig


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

    def extract_payload_from_token(self, token: str, is_socket: bool = False):
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


@dataclass(frozen=True)
class UserRealm:
    username: str = None
    email: str = None
    nox_id: str = None
