import abc
from typing import Optional

from sqlalchemy import delete, insert, select, update

from app.core.config import ApiConfig
from app.database.sql_client import SQLClient
from app.utils.auth_utils import AuthUtils, UserRealm


class BaseRepository(abc.ABC):
    def __init__(self, sql_client: SQLClient, api_config: Optional[ApiConfig] = None):
        self.client_factory = sql_client
        self.api_config = api_config

    @SQLClient.handle_session
    def insert_one(self, query, model, session=None):
        stmt = insert(model).values(
            query
        )  # destructure this value in parent if it's a Schema model
        result = session.execute(stmt)
        session.commit()
        (key,) = result.inserted_primary_key
        return key

    @SQLClient.handle_session
    def get_one(self, query, query_field, model, session=None):
        stmt = select(model).where(getattr(model, query_field) == query)
        result = session.execute(stmt)
        return result.scalars().one_or_none()

    @SQLClient.handle_session
    def execute_raw(self, stmt, commit: bool = False, session=None):
        result = session.execute(stmt)
        if commit:
            session.commit()
        return result.fetchall()

    @SQLClient.handle_session
    def get_one_by_query(self, query, model, session=None):
        stmt = select(model).where(query)
        result = session.execute(stmt)
        return result.scalars().one_or_none()

    @SQLClient.handle_session
    def update_one(self, query, update_values, model, session=None):
        stmt = update(model).where(query).values(update_values)
        session.execute(stmt)
        session.commit()
        return

    @SQLClient.handle_session
    def delete_one(self, query, model, session=None):
        stmt = delete(model).where(query)
        session.execute(stmt)
        session.commit()
        return


class BoundRepository(BaseRepository):
    # TODO: Update when bounding clients
    def __init__(
        self,
        user_realm: UserRealm,
        api_config: Optional[ApiConfig] = None,
        sql_client: SQLClient = None,
        auth_utils: AuthUtils = None,
    ):
        self.user_realm = user_realm
        self.auth_utils = auth_utils
        super().__init__(sql_client=sql_client, api_config=api_config)
