from typing import List

from fastapi import APIRouter
from starlette import status

from app.core.request import ReqDep
from app.models.friends import FriendsResponse
from app.repository.friends.friends import FriendsRepository

router = APIRouter()


@router.get(
    "/search/{nox_id}", status_code=status.HTTP_200_OK, response_model=FriendsResponse
)
def search_friend(
    nox_id: str, friends_repo: FriendsRepository = ReqDep(FriendsRepository)
):
    response = friends_repo.search(nox_id)
    return response


@router.get("", status_code=status.HTTP_200_OK, response_model=List[FriendsResponse])
def get_friends(friends_repo: FriendsRepository = ReqDep(FriendsRepository)):
    response = friends_repo.get_accepted_friends()
    return response


@router.get(
    "/pending", status_code=status.HTTP_200_OK, response_model=List[FriendsResponse]
)
def get_pending_requests(friends_repo: FriendsRepository = ReqDep(FriendsRepository)):
    response = friends_repo.get_pending_friends()
    return response


@router.get(
    "/blocked", status_code=status.HTTP_200_OK, response_model=List[FriendsResponse]
)
def get_blocked_requests(friends_repo: FriendsRepository = ReqDep(FriendsRepository)):
    response = friends_repo.get_blocked_friends()
    return response


@router.post("/add/{nox_id}", status_code=status.HTTP_200_OK)
def add_new_friend(
    nox_id: str,
    friends_repo: FriendsRepository = ReqDep(FriendsRepository),
):
    response = friends_repo.add_friend(nox_id)
    return response


@router.put("/accept/{nox_id}", status_code=status.HTTP_200_OK)
def accept_friend(
    nox_id: str,
    friends_repo: FriendsRepository = ReqDep(FriendsRepository),
):
    response = friends_repo.accept(nox_id)
    return response


@router.put("/reject/{nox_id}", status_code=status.HTTP_200_OK)
def reject_friend(
    nox_id: str,
    friends_repo: FriendsRepository = ReqDep(FriendsRepository),
):
    response = friends_repo.reject(nox_id)
    return response


@router.delete("/remove/{nox_id}", status_code=status.HTTP_200_OK)
def remove_friend(
    nox_id: str,
    friends_repo: FriendsRepository = ReqDep(FriendsRepository),
):
    response = friends_repo.delete(nox_id)
    return response


@router.put("/block/{nox_id}", status_code=status.HTTP_200_OK)
def block_friend(
    nox_id: str,
    friends_repo: FriendsRepository = ReqDep(FriendsRepository),
):
    response = friends_repo.block(nox_id)
    return response


@router.put("/unblock/{nox_id}", status_code=status.HTTP_200_OK)
def unblock_friend(
    nox_id: str,
    friends_repo: FriendsRepository = ReqDep(FriendsRepository),
):
    response = friends_repo.unblock(nox_id)
    return response
