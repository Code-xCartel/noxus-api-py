from fastapi import APIRouter, Request
from starlette import status
from typing import List

from app.core.container import reqDep
from app.models.friends import FriendsResponse
from app.repository.friends.friends import FriendsRepository

router = APIRouter()


@router.get(
    "/search/{nox_id}", status_code=status.HTTP_200_OK, response_model=FriendsResponse
)
def search_friend(
    nox_id: str, friends_repo: FriendsRepository = reqDep(FriendsRepository)
):
    response = friends_repo.search(nox_id)
    return response


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[FriendsResponse])
def get_friends(
    request: Request, friends_repo: FriendsRepository = reqDep(FriendsRepository)
):
    response = friends_repo.get_accepted_friends(request)
    return response


@router.post("/add/{nox_id}", status_code=status.HTTP_200_OK)
def add_new_friend(
    request: Request,
    nox_id: str,
    friends_repo: FriendsRepository = reqDep(FriendsRepository),
):
    response = friends_repo.add_friend(request, nox_id)
    return response


@router.put("/accept/{nox_id}", status_code=status.HTTP_200_OK)
def accept_friend(
    request: Request,
    nox_id: str,
    friends_repo: FriendsRepository = reqDep(FriendsRepository),
):
    response = friends_repo.accept(request, nox_id)
    return response
