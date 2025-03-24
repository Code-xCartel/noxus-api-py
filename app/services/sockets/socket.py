from fastapi import WebSocket, WebSocketException
from starlette.websockets import WebSocketDisconnect

from app.core.container import reqDep
from app.repository.friends.friends import FriendsRepository
from app.repository.sockets.status.status import StatusRepository, Status

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
    status_repository: StatusRepository = reqDep(StatusRepository),
    friends_repository: FriendsRepository = reqDep(FriendsRepository),
):
    try:
        await status_repository.authorize_and_connect(
            websocket, fr_repo=friends_repository
        )
        await status_repository.get_all_status(friends_repository)
    except Exception as e:
        print(str(e), "error")
        raise WebSocketException(code=1008, reason=str(e))

    try:
        while True:
            data = await websocket.receive_text()
            await status_repository.change_status(
                Status.getStatusType(data), friends_repository
            )
    except WebSocketDisconnect as e:
        print(str(e), 'disconnected from client side probably')
        await status_repository.disconnect()
