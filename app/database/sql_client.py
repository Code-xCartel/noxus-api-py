from app.database.database import Database
from concurrent.futures import ThreadPoolExecutor


executor = ThreadPoolExecutor(max_workers=5)


class SQLClient:
    def __init__(self, db: Database):
        self.db = db

    @staticmethod
    def handle_session(func):
        def wrapper(self, *args, **kwargs):
            with self.client_factory.db.session as session:
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
