from enum import Enum

from fastapi import HTTPException, Request
from starlette import status
from sqlalchemy import and_, or_, select
from typing import List

from app.core.mixin import RepoHelpersMixin
from app.schemas.schemas import Friends, User
from app.utils.strings import JSONResponse


class Status(Enum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    PENDING = "pending"
    BLOCKED = "blocked"


class FriendsRepository(RepoHelpersMixin):
    @staticmethod
    def create_get_query(user_id: str, st: Status):
        stmt = (
            select(User.nox_id, User.username, Friends.status)
            .join(
                Friends,
                or_(User.nox_id == Friends.friend_id, User.nox_id == Friends.user_id),
            )
            .where(
                or_(Friends.user_id == user_id, Friends.friend_id == user_id),
                Friends.status == st.value,
            )
        )

        if st.value == "blocked":
            stmt = stmt.where(Friends.action_by == user_id)

        return stmt

    @staticmethod
    def create_action_query(user_id: str, friend_id: str, st: List[str]):
        return and_(
            or_(
                and_(Friends.user_id == user_id, Friends.friend_id == friend_id),
                and_(Friends.user_id == friend_id, Friends.friend_id == user_id),
            ),
            Friends.status.in_(st),
        )

    @staticmethod
    def create_or_query(user_id: str, friend_id: str):
        stmt = or_(
            and_(Friends.user_id == user_id, Friends.friend_id == friend_id),
            and_(Friends.user_id == friend_id, Friends.friend_id == user_id),
        )
        return stmt

    def get_accepted_friends(self, request: Request):
        self_id = request.state.payload["nox_id"]
        friends =  self.repo.execute_raw(
            stmt=self.create_get_query(user_id=self_id, st=Status.ACCEPTED)
        )
        filtered_friends = [item for item in friends if item[0] != self_id]
        return filtered_friends

    def get_pending_friends(self, request: Request):
        self_id = request.state.payload["nox_id"]
        friends =  self.repo.execute_raw(
            stmt=self.create_get_query(user_id=self_id, st=Status.PENDING)
        )
        filtered_friends = [item for item in friends if item[0] != self_id]
        return filtered_friends

    def get_blocked_friends(self, request: Request):
        self_id = request.state.payload["nox_id"]
        friends =  self.repo.execute_raw(
            stmt=self.create_get_query(user_id=self_id, st=Status.BLOCKED)
        )
        filtered_friends = [item for item in friends if item[0] != self_id]
        return filtered_friends

    def add_friend(self, request: Request, nox_id: str):
        self_id = request.state.payload["nox_id"]
        friend =  self.get_one(query=nox_id, query_field="nox_id", model=User)
        if not friend or self_id == nox_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Invalid nox id"
            )
        relation =  self.get_one_by_query(
            query=self.create_or_query(user_id=self_id, friend_id=nox_id),
            model=Friends,
        )
        if relation:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Request already exists"
            )
        query = {
            "user_id": self_id,
            "friend_id": nox_id,
            "status": Status.PENDING.value,
        }
        _ = self.insert_one(query=query, model=Friends)
        return JSONResponse(details="Request sent")

    def search(self, nox_id: str):
        user =  self.get_one(query=nox_id, query_field="nox_id", model=User)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Invalid nox id"
            )
        return user

    def accept(self, request: Request, nox_id: str):
        self_id = request.state.payload["nox_id"]
        user =  self.get_one(query=nox_id, query_field="nox_id", model=User)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Invalid nox id"
            )
        query = self.create_action_query(
            user_id=self_id, friend_id=nox_id, st=[Status.PENDING.value]
        )
        values = {"status": Status.ACCEPTED.value, "action_by": self_id}
        _ =  self.update_one(query=query, model=Friends, update_values=values)
        return JSONResponse(details="Request accepted")

    def reject(self, request: Request, nox_id: str):
        self_id = request.state.payload["nox_id"]
        user =  self.get_one(query=nox_id, query_field="nox_id", model=User)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Invalid nox id"
            )
        query =  self.create_action_query(
            user_id=self_id, friend_id=nox_id, st=[Status.PENDING.value]
        )
        values = {"status": Status.REJECTED.value, "action_by": self_id}
        _ =  self.update_one(query=query, model=Friends, update_values=values)
        query = self.create_or_query(user_id=self_id, friend_id=nox_id)
        _ =  self.delete_one(query=query, model=Friends)
        return JSONResponse(details="Request rejected")

    def delete(self, request: Request, nox_id: str):
        self_id = request.state.payload["nox_id"]
        user =  self.get_one(query=nox_id, query_field="nox_id", model=User)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Invalid nox id"
            )
        query = self.create_or_query(user_id=self_id, friend_id=nox_id)
        _ =  self.delete_one(query=query, model=Friends)
        return JSONResponse(details="Request deleted")

    def block(self, request: Request, nox_id: str):
        self_id = request.state.payload["nox_id"]
        user =  self.get_one(query=nox_id, query_field="nox_id", model=User)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Invalid nox id"
            )
        query = self.create_action_query(
            user_id=self_id,
            friend_id=nox_id,
            st=[Status.PENDING.value, Status.ACCEPTED.value],
        )
        values = {"status": Status.BLOCKED.value, "action_by": self_id}
        _ =  self.update_one(query=query, model=Friends, update_values=values)
        return JSONResponse(details="Request blocked")

    def unblock(self, request: Request, nox_id: str):
        self_id = request.state.payload["nox_id"]
        user =  self.get_one(query=nox_id, query_field="nox_id", model=User)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Invalid nox id"
            )
        query = self.create_action_query(
            user_id=self_id, friend_id=nox_id, st=[Status.BLOCKED.value]
        )
        values = {"status": Status.ACCEPTED.value, "action_by": self_id}
        _ =  self.update_one(query=query, model=Friends, update_values=values)
        return JSONResponse(details="Request unblocked")
