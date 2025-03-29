from typing import Callable

from fastapi import Depends, Request
from starlette.websockets import WebSocket


def _create_req_dep():
    def req_dep(dependency: Callable, **kwargs):
        def resolver(request: Request = None, websocket: WebSocket = None):
            request = request or websocket
            if not hasattr(request.state, "dep_container"):
                request.state.dep_container = request.app.create_container_from_request(
                    request
                )

            return request.state.dep_container.resolve(dependency)

        return Depends(resolver, **kwargs)

    return req_dep


ReqDep = _create_req_dep()
