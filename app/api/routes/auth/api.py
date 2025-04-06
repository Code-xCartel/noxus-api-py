from fastapi import APIRouter, HTTPException
from starlette import status

from app.core.request import ReqDep
from app.exceptions.exceptions import EmailException
from app.models.user import LoginResponse, UserIn
from app.repository.auth.auth import AuthorizationRepository
from app.services.emails.email_service import AuthEmailService
from app.utils.strings import JSONResponse

router = APIRouter()


# TODO: sig verification for all auth routes
@router.post("/register", status_code=status.HTTP_200_OK)
def register(
    request: UserIn,
    auth_repo: AuthorizationRepository = ReqDep(AuthorizationRepository),
    email_svc: AuthEmailService = ReqDep(AuthEmailService),
):
    auth_repo.check_existing_user(request)
    try:
        email_svc.configure_auth_mail(request)
        email_svc.send_mail()
    except EmailException as e:
        raise HTTPException(
            status_code=status.HTTP_417_EXPECTATION_FAILED, detail=str(e)
        )
    return JSONResponse(details="Email sent successfully")


@router.post("/login", status_code=status.HTTP_200_OK, response_model=LoginResponse)
def login(
    request: UserIn,
    auth_repo: AuthorizationRepository = ReqDep(AuthorizationRepository),
):
    response = auth_repo.authenticate_user(request)
    return response
