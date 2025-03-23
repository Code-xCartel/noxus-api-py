from typing import Dict
from enum import Enum

from fastapi import WebSocketException
from jose import jwt, JWTError
from starlette.websockets import WebSocket

from app.core.mixin import RepoHelpersMixin
from app.middleware.authorization import TOKEN
from app.repository.friends.friends import FriendsRepository
from pydantic import BaseModel


class Status(Enum):
    ONLINE = "online"
    AWAY = "away"
    OFFLINE = "offline"

    @staticmethod
    def getStatusType(data):
        if data == "online":
            return Status.ONLINE
        elif data == "away":
            return Status.AWAY
        else:
            return Status.OFFLINE


class Client(BaseModel):
    socket: WebSocket
    status: Status

    class Config:
        arbitrary_types_allowed = True


class WebSocketService(RepoHelpersMixin):
    clients: Dict[str, Client] = {}

    async def authorize_and_connect(self, socket: WebSocket):
        path = socket.url.path
        for path_regex in self.request.app.config.SKIP_AUTH_ROUTES:
            if path_regex.match(path):
                return await self.connect(socket)

        token = socket.headers.get("Authorization")
        if not token:
            raise WebSocketException(code=1008, reason="Authorization header required")
        identity, key = token.split()
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
            return await self.connect(socket)
        except JWTError as e:
            raise WebSocketException(
                code=1008, reason=f"Could not validate token, {str(e)}"
            )

    async def connect(self, socket: WebSocket):
        await socket.accept()
        nox_id = self.request.state.payload["nox_id"]
        status = self.request.headers.get("Status") or "online"
        self.clients[nox_id] = Client(
            socket=socket, status=Status.getStatusType(status)
        )
        await self.clients[nox_id].socket.send_text(
            f"Websocket Connected: {nox_id}, Status: {status}"
        )

    async def disconnect(self):
        nox_id = self.request.state.payload["nox_id"]
        await self.clients[nox_id].socket.send_text(f"Websocket Disconnected: {nox_id}")
        await self.clients[nox_id].socket.close()
        del self.clients[nox_id]

    async def cast_to(self, nox_id, message: str):
        conn = self.clients[nox_id]
        await conn.send_text(message)

    async def broadcast(self, message, to: Dict[str, Client] = None):
        clients_to_broadcast = to if to else self.clients
        for nox_id, client in clients_to_broadcast.items():
            print(f"Broadcasting message to {nox_id}")
            await client.socket.send_text(message)

    async def get_all_status(self, repo: FriendsRepository):
        nox_id = self.request.state.payload["nox_id"]
        my_friends = repo.get_accepted_friends(self.request)
        friend_ids = {friend[0] for friend in my_friends}
        all_status = {
            nox_id: client.status.value
            for nox_id, client in self.clients.items()
            if nox_id in friend_ids
        }
        await self.clients[nox_id].socket.send_text(str(all_status))

    async def change_status(self, status: Status, repo: FriendsRepository):
        nox_id = self.request.state.payload["nox_id"]
        my_friends = repo.get_accepted_friends(self.request)
        friend_ids = {friend[0] for friend in my_friends}
        instance = self.clients[nox_id]
        instance.status = status
        broadcast_to = {
            nox_id: client
            for nox_id, client in self.clients.items()
            if nox_id in friend_ids
        }
        message = str(
            {
                "noxId": nox_id,
                "status": self.clients[nox_id].status.value,
            }
        )
        await self.broadcast(message=message, to=broadcast_to)
