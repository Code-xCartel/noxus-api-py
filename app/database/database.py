import logging

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, scoped_session, sessionmaker

from app.core.config import ApiConfig

logger = logging.getLogger(__name__)

Base = declarative_base()


class Database:
    _instance = None
    _engine = None

    def __new__(
        cls, api_config: ApiConfig, echo: bool = False, echo_pool: bool = False
    ) -> "Database":
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            logger.info("Initializing Postgres Engine")
            cls._engine = create_engine(
                api_config.DB_PG_URL, echo=echo, echo_pool=echo_pool
            )
        return cls._instance

    def __init__(
        self, api_config: ApiConfig, echo: bool = False, echo_pool: bool = False
    ) -> None:
        pass

    def resolve_session(self) -> Session:
        return scoped_session(
            sessionmaker(
                bind=self._engine,
                autoflush=False,
                autocommit=False,
                expire_on_commit=False,
            )
        )()
