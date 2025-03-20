from typing import Union

from pydantic import BaseModel, Field


class FriendsResponse(BaseModel):
    nox_id: str = Field(alias="noxId")
    username: str
    avatar: Union[str, None] = None

    class Config:
        populate_by_name = True
