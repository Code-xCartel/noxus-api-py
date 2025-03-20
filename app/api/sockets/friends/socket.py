from fastapi import APIRouter
from starlette.websockets import WebSocket

router = APIRouter()


@router.websocket("/ws")
async def status_socket(websocket: WebSocket):
    await websocket.accept()
    while True:
        message = await websocket.receive_text()
        await websocket.send_text(message)
