from enum import Enum

from fastapi import Request, HTTPException
from jose import jwt, JWTError
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class TOKEN(Enum):
    BEARER = "Bearer"


class AuthorizationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, _app):
        super().__init__(app)
        self._app = _app

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        for path_regex in self._app.config.SKIP_AUTH_ROUTES:
            if path_regex.match(path):
                return await call_next(request)

        token = request.headers.get("Authorization")
        if not token:
            return JSONResponse(
                content={"details": "Authorization header required"},
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        identity, key = token.split()
        if not identity or not key:
            return JSONResponse(
                content={"details": "Token must have two element"},
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        if identity != TOKEN.BEARER.value:
            return JSONResponse(
                content={"details": "Invalid auth scheme"},
            )

        try:
            payload = jwt.decode(
                key,
                self._app.config.JWT_SECRET_KEY,
                algorithms=[self._app.config.JWT_ALGORITHM],
            )
            request.state.payload = payload
            return await call_next(request)
        except JWTError as e:
            return JSONResponse(
                content={"details": "Could not validate token"},
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
