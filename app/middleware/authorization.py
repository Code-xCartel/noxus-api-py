from fastapi import Request
from socketio import ASGIApp
from starlette.authentication import AuthenticationError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import ApiConfig
from app.utils.auth_utils import AuthUtils


class AuthorizationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, config: ApiConfig, auth_utils: AuthUtils):
        self.config = config
        self.auth_utils = auth_utils
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        request.state.user = None
        path = request.url.path
        for path_regex in self.config.SKIP_AUTH_ROUTES:
            if path_regex.match(path):
                return await call_next(request)
        try:
            identity, key = self.auth_utils.validate_request(request)
            self.auth_utils.validate_scheme(identity)
            payload = self.auth_utils.extract_payload_from_token(key)
            request.state.user = payload
            return await call_next(request)
        except AuthenticationError as e:
            return JSONResponse(status_code=401, content={"details": str(e)})


class WSAuthorizationMiddleware:
    def __init__(self, app: ASGIApp, auth_utils: AuthUtils):
        self.app = app
        self.auth_utils = auth_utils

    async def __call__(self, scope, receive, send):
        if scope["type"] != "websocket":
            return await self.app(scope, receive, send)

        try:
            scope_d = dict(scope.get("headers"))
            auth_header = scope_d.get(b'authorization', b'').decode()  # fmt: off
            identity, key = self.auth_utils.validate_request(header=auth_header)
            self.auth_utils.validate_scheme(identity)
            payload = self.auth_utils.extract_payload_from_token(key)
            scope["state"]["user"] = payload
            return await self.app(scope, receive, send)
        except AuthenticationError as e:
            await send({"type": "websocket.accept"})  # Accept the connection
            await send({"type": "websocket.close", "code": 1008})  # Then close
