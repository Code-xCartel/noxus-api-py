# from typing import Dict
# from enum import Enum
# from pydantic import BaseModel
# from starlette.websockets import WebSocket
#
# from app.core.mixin import RepoHelpersMixin
#
#
# class Status(Enum):
#     ONLINE = "online"
#     AWAY = "away"
#     OFFLINE = "offline"
#
# class Client(BaseModel):
#     status: Status
#     socket: WebSocket
#
#
# class WebSocketService(RepoHelpersMixin):
#     def __init__(self):
#         self.clients: Dict[str, Client] = {}
#
#     async def connect(self):
#         return "hi"
