from fastapi import WebSocket, WebSocketException
from starlette.websockets import WebSocketDisconnect

from app.core.container import reqDep
from app.repository.friends.friends import FriendsRepository
from app.services.websocket_service import WebSocketService, Status

ws_routes = []


def websocket_route(path: str):
    """Decorator to register WebSocket routes."""

    def decorator(func):
        ws_routes.append((f"/ws{path}", func))
        return func

    return decorator


@websocket_route("/status")
async def websocket_status(
    websocket: WebSocket,
    websocket_service: WebSocketService = reqDep(WebSocketService),
    friends_repository: FriendsRepository = reqDep(FriendsRepository),
):
    try:
        await websocket_service.authorize_and_connect(websocket)
        await websocket_service.get_all_status(friends_repository)
    except Exception as e:
        raise WebSocketException(code=1008, reason=str(e))

    try:
        while True:
            data = await websocket.receive_text()
            await websocket_service.change_status(
                Status.getStatusType(data), friends_repository
            )
    except WebSocketDisconnect:
        await websocket_service.disconnect()
