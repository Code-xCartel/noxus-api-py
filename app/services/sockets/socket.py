from fastapi import APIRouter, WebSocket, WebSocketException
from starlette.websockets import WebSocketDisconnect

from app.core.request import ReqDep
from app.repository.sockets.status.status import Status, StatusRepository

router = APIRouter()


@router.websocket("/status")
async def websocket_status(
    *,
    websocket: WebSocket,
    status_repository: StatusRepository = ReqDep(StatusRepository),
):
    await status_repository.connect(socket=websocket)
    await status_repository.get_all_status()

    while True:
        try:
            data = await websocket.receive_text()
            await status_repository.change_status(Status.getStatusType(data))
        except WebSocketDisconnect as e:
            await status_repository.disconnect()
            raise WebSocketException(code=1005, reason=str(e))
        except Exception as e:
            await status_repository.disconnect()
            raise WebSocketException(code=1005, reason=str(e))
