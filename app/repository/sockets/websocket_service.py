from typing import Dict, Any

from fastapi import WebSocketException
from jose import jwt, JWTError
from starlette.websockets import WebSocket

from app.core.mixin import RepoHelpersMixin
from app.middleware.authorization import TOKEN
from pydantic import BaseModel


class Client(BaseModel):
    socket: WebSocket
    payload: Any

    class Config:
        arbitrary_types_allowed = True


class WebSocketService(RepoHelpersMixin):
    clients: Dict[str, Client] = {}

    async def authorize_and_connect(self, socket: WebSocket, **kwargs):
        path = socket.url.path
        for path_regex in self.request.app.config.SKIP_AUTH_ROUTES:
            if path_regex.match(path):
                return await self.connect(socket)

        key = socket.query_params.get("tk")
        identity = socket.query_params.get("sh")
        if not identity or not key:
            raise WebSocketException(code=1008, reason="Token must have two element")
        if identity != TOKEN.BEARER.value:
            raise WebSocketException(code=1008, reason="Invalid auth scheme")

        try:
            payload = jwt.decode(
                key,
                self.request.app.config.JWT_SECRET_KEY,
                algorithms=[self.request.app.config.JWT_ALGORITHM],
            )
            socket.state.payload = payload
            return await self.connect(socket, **kwargs)
        except JWTError as e:
            raise WebSocketException(
                code=1008, reason=f"Could not validate token, {str(e)}"
            )

    async def connect(self, socket: WebSocket, payload: Any = None):
        await socket.accept()
        nox_id = self.request.state.payload["nox_id"]
        status = self.request.query_params.get("st") or "online"
        self.clients[nox_id] = Client(socket=socket, payload=payload)
        await self.clients[nox_id].socket.send_text(
            f"Websocket Connected: {nox_id}, Status: {status}"
        )

    async def disconnect(self):
        nox_id = self.request.state.payload["nox_id"]
        # await self.clients[nox_id].socket.send_text(f"Websocket Disconnected: {nox_id}")
        await self.clients[nox_id].socket.close()
        del self.clients[nox_id]

    async def cast_to(self, nox_id, message: str):
        conn = self.clients[nox_id]
        await conn.send_text(message)

    async def broadcast(
        self, message, to: Dict[str, Client] = None, is_explicit: bool = False
    ):
        clients_to_broadcast = self.clients if not to and not is_explicit else to
        for nox_id, client in clients_to_broadcast.items():
            print(f"Broadcasting message to {nox_id}")
            await client.socket.send_text(message)
