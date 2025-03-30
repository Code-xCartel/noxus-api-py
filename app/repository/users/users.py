import httpx

from app.core.mixin import RepoHelpersMixin
from app.models.user import AvatarUpdate, UsernameUpdate
from app.schemas.schemas import User


class UsersRepository(RepoHelpersMixin):
    def change_username(self, username: UsernameUpdate) -> None:
        nox_id = self.nox_id
        query = User.nox_id == nox_id
        self.update_one(model=User, query=query, update_values=username.model_dump())
        return

    def change_avatar(self, avatar: AvatarUpdate) -> None:
        nox_id = self.nox_id
        query = User.nox_id == nox_id
        self.update_one(model=User, query=query, update_values=avatar.model_dump())
        return

    async def get_avatars(self, search_term: str):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.api_config.GIPHY_BASE_URL,
                params={
                    "q": search_term,
                    "api_key": self.api_config.GIPHY_API_KEY,
                    "limit": self.api_config.GIPHY_RESPONSE_LIMIT,
                    "offset": 0,
                    "rating": "g",
                    "lang": "en",
                    "bundle": "messaging_non_clips",
                },
            )
            return response.json()["data"]
