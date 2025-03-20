import abc
from app.database.sql_client import SQLClient
from sqlalchemy import insert, select, text, update, delete


class BaseRepository(abc.ABC):
    client_factory = None

    def __init__(self, sql_client: SQLClient):
        if self.client_factory is None:
            self.client_factory = sql_client

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
        result = session.execute(stmt)
        session.commit()
        return

    @SQLClient.handle_session
    def delete_one(self, query, model, session=None):
        stmt = delete(model).where(query)
        result = session.execute(stmt)
        session.commit()
        return


class BoundRepository(BaseRepository):
    def __init__(self, sql_client: SQLClient):
        super().__init__(sql_client)
