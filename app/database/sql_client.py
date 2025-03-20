from contextlib import contextmanager

from app.database.database import Database
from concurrent.futures import ThreadPoolExecutor


executor = ThreadPoolExecutor(max_workers=5)


class SQLClient:
    _client_engine = None

    def __init__(self, db: Database):
        self.db = db
        SQLClient._client_engine = Database.engine

    @staticmethod
    def handle_session(func):
        def wrapper(self, *args, **kwargs):
            with Database.resolve_session(SQLClient._client_engine) as session:
                try:
                    # only use positional arguments in mixin function
                    result = func(self, session=session, **kwargs)
                    return result
                except Exception as e:
                    session.rollback()
                    raise e
                finally:
                    session.close()

        return wrapper
