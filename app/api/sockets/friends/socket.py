# from fastapi import APIRouter
# from starlette.websockets import WebSocket
#
# from app.core.container import reqDep
# from app.services.websocket_service import WebSocketService
#
# socket = APIRouter()
#
#
# @socket.websocket("/status/ws")
# async def status_socket(websocket: WebSocketService = reqDep(WebSocketService)):
#     await websocket.connect()
#     return "Hi"
