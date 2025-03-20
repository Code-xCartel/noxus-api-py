import logging

from sqlalchemy import create_engine, Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker, scoped_session

logger = logging.getLogger(__name__)

Base = declarative_base()


class Database:
    engine = None

    def __init__(
        self, db_url: str, echo: bool = False, echo_pool: bool = False
    ) -> None:
        if Database.engine is None:
            logger.info("Initializing Postgres Engine")
            self._engine = create_engine(db_url, echo=echo, echo_pool=echo_pool)
            Database.engine = self._engine

    @staticmethod
    def resolve_session(engine: Engine) -> Session:
        return scoped_session(sessionmaker(
            bind=engine, autoflush=False, autocommit=False, expire_on_commit=False
        ))()
