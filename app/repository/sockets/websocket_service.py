from typing import Dict, Any
from pydantic import BaseModel
from fastapi import WebSocketException
from starlette.websockets import WebSocket

from app.core.mixin import RepoHelpersMixin
from app.utils.auth_utils import AuthScheme


class Client(BaseModel):
    socket: WebSocket
    payload: Any

    class Config:
        arbitrary_types_allowed = True


"""
TODO: Websockets are not a part of ASGI app, so they wont pass through the container cloning stage,
    which means bound repository was never resolved, i need to figure out a way to resolve those dependencies 
    manually
"""


class WebSocketService(RepoHelpersMixin):
    clients: Dict[str, Client] = {}

    async def connect(self, socket: WebSocket, payload: Any = None):
        await socket.accept()
        nox_id = self.nox_id
        self.clients[nox_id] = Client(socket=socket, payload=payload)
        await self.clients[nox_id].socket.send_text(f"Websocket Connected: {nox_id}")

    async def disconnect(self):
        nox_id = self.nox_id
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
