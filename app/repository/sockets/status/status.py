from enum import Enum
from typing import Any

from starlette.websockets import WebSocket

from app.repository.friends.friends import FriendsRepository
from app.repository.sockets.websocket_service import WebSocketService


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

class StatusRepository(WebSocketService):

    async def connect(self, socket: WebSocket, payload: Any = None, **kwargs):
        status = self.request.headers.get("Status") or "online"
        status = Status.getStatusType(status)
        await super().connect(socket, payload={ 'status': status })
        await self.change_status(status, kwargs['fr_repo'])

    async def get_all_status(self, repo: FriendsRepository):
        nox_id = self.request.state.payload["nox_id"]
        my_friends = repo.get_accepted_friends(self.request)
        friend_ids = {friend[0] for friend in my_friends}
        all_status = [
            {'noxId': nox_id, 'status': client.payload['status'].value}
            for nox_id, client in self.clients.items()
            if nox_id in friend_ids
        ]
        await self.clients[nox_id].socket.send_text(str(all_status))

    async def change_status(self, status: Status, repo: FriendsRepository):
        nox_id = self.request.state.payload["nox_id"]
        my_friends = repo.get_accepted_friends(self.request)
        friend_ids = {friend[0] for friend in my_friends}
        instance = self.clients[nox_id]
        instance.payload['status'] = status
        broadcast_to = {
            nox_id: client
            for nox_id, client in self.clients.items()
            if nox_id in friend_ids
        }
        message = str(
            {
                "noxId": nox_id,
                "status": self.clients[nox_id].payload['status'].value,
            }
        )
        await self.broadcast(message=message, to=broadcast_to, is_explicit=True)