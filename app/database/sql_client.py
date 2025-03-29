from concurrent.futures import ThreadPoolExecutor

from app.database.database import Database

executor = ThreadPoolExecutor(max_workers=5)


class SQLClient:
    client_engine = None

    def __init__(self, db: Database):
        self.client_engine = db

    @staticmethod
    def handle_session(func):
        def wrapper(self, *args, **kwargs):
            with self.client_factory.client_engine.resolve_session() as session:
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
