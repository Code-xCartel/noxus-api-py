from fastapi import APIRouter
from app.api.routes.auth.api import router as auth_router
from app.api.routes.friends.api import router as friend_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(friend_router, prefix="/friends", tags=["friends"])
