from fastapi import APIRouter
from starlette import status

from app.core.container import reqDep
from app.models.user import UserInExtended, UserIn, LoginResponse
from app.repository.auth.auth import AuthorizationRepository

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(
    request: UserInExtended,
    auth_repo: AuthorizationRepository = reqDep(AuthorizationRepository),
):
    response = auth_repo.create_user(request)
    return response


@router.post("/login", status_code=status.HTTP_200_OK, response_model=LoginResponse)
def login(
    request: UserIn,
    auth_repo: AuthorizationRepository = reqDep(AuthorizationRepository),
):
    response = auth_repo.authenticate_user(request)
    return response
