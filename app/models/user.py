from typing import Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field


class EmailIn(BaseModel):
    email: str


class UserIn(EmailIn):
    password: str = Field(min_length=8)


class UserInExtended(UserIn):
    username: str
    avatar: Optional[str] = None


class UsernameUpdate(BaseModel):
    username: str


class PasswordUpdate(BaseModel):
    password_new: str = Field(alias="passwordNew", min_length=8)
    password_old: str = Field(alias="passwordOld")


class AvatarUpdate(BaseModel):
    avatar: str


class UserOut(BaseModel):
    id: UUID
    email: str
    nox_id: str = Field(alias="noxId")
    username: str
    avatar: Union[str, None] = None

    class Config:
        populate_by_name = True


class LoginResponse(BaseModel):
    access_token: str = Field(alias="accessToken")
    token_type: str = Field(alias="tokenType")
    user: UserOut

    class Config:
        populate_by_name = True


class AvatarsSearchResponse(BaseModel):
    id: str
    slug: str
    title: str
    rating: str
    images: dict
    alt_text: str = Field(alias="altText")

    class Config:
        populate_by_name = True


class WorkflowIn(BaseModel):
    pkt: str
    sig: str
