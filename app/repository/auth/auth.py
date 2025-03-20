from datetime import datetime, timedelta
from starlette import status
from fastapi import HTTPException
from jose import jwt
from app.core.mixin import RepoHelpersMixin
from app.models.user import UserInExtended, UserIn
from app.schemas.schemas import User
from app.utils.strings import generate_unique_id, JSONResponse
from passlib.context import CryptContext

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthorizationRepository(RepoHelpersMixin):
    async def find_user_by_field(
        self, query: str, field: str, skip_check: bool = False
    ) -> User:
        user = await self.get_one(query=query, query_field=field, model=User)
        if not skip_check and not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return user

    async def create_user(self, user: UserInExtended):
        user_dump = user.model_dump()
        existing_user = await self.find_user_by_field(
            query=user_dump["email"], field="email", skip_check=True
        )
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="User already exists"
            )
        user_dump["nox_id"] = generate_unique_id()
        user_dump["password"] = bcrypt_context.hash(user_dump["password"])
        key = await self.insert_one(query=user_dump, model=User)
        return JSONResponse(details=f"User created successfully {key}")

    async def authenticate_user(self, user: UserIn):
        existing_user = await self.find_user_by_field(query=user.email, field="email")
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        if not bcrypt_context.verify(user.password, existing_user.password):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Incorrect password"
            )
        encode = {
            "email": existing_user.email,
            "username": existing_user.username,
            "nox_id": existing_user.nox_id,
        }
        expires = datetime.utcnow() + timedelta(
            days=int(self.api_config.JWT_EXPIRATION_DELTA)
        )
        encode.update({"exp": expires})
        return {
            "access_token": jwt.encode(
                encode,
                self.api_config.JWT_SECRET_KEY,
                algorithm=self.api_config.JWT_ALGORITHM,
            ),
            "token_type": "bearer",
            "user": existing_user,
        }
