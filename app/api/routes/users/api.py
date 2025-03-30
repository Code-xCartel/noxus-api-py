from typing import List

from fastapi import APIRouter

from app.core.request import ReqDep
from app.models.user import AvatarsSearchResponse, AvatarUpdate, UsernameUpdate
from app.repository.users.users import UsersRepository

router = APIRouter()


@router.post("/update-username")
def update_username(
    username: UsernameUpdate, user_repo: UsersRepository = ReqDep(UsersRepository)
):
    return user_repo.change_username(username)


@router.post("/update-avatar")
def update_avatar(
    avatar: AvatarUpdate, user_repo: UsersRepository = ReqDep(UsersRepository)
):
    return user_repo.change_avatar(avatar)


@router.get("/avatars", response_model=List[AvatarsSearchResponse])
async def get_avatars(
    search: str, user_repo: UsersRepository = ReqDep(UsersRepository)
):
    return await user_repo.get_avatars(search_term=search)
