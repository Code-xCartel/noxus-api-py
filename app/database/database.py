import logging

from sqlalchemy import create_engine, Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker, scoped_session

from app.core.config import ApiConfig

logger = logging.getLogger(__name__)

Base = declarative_base()


class Database:
    engine = None

    def __init__(
        self, api_config: ApiConfig, echo: bool = False, echo_pool: bool = False
    ) -> None:
        db_url = api_config.DB_PG_URL
        if Database.engine is None:
            logger.info("Initializing Postgres Engine")
            self.engine = create_engine(db_url, echo=echo, echo_pool=echo_pool)

    def resolve_session(self) -> Session:
        return scoped_session(
            sessionmaker(
                bind=self.engine,
                autoflush=False,
                autocommit=False,
                expire_on_commit=False,
            )
        )()
