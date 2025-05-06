import logging
from typing import Dict

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
            cls._instance.api_config = api_config
            logger.info("Initializing Postgres Engine")
            cls._engine = create_engine(
                api_config.DB_PG_URL, echo=echo, echo_pool=echo_pool
            )
        return cls._instance

    def __init__(
        self, api_config: ApiConfig, echo: bool = False, echo_pool: bool = False
    ) -> None:
        pass

    def _get_schema_translate_map(self) -> Dict:
        schema_translate_map = {None: self.api_config.SCHEMA}
        return schema_translate_map

    def resolve_session(self) -> Session:
        schema_translated_engine = self._engine.execution_options(
            schema_translate_map=self._get_schema_translate_map()
        )
        return scoped_session(
            sessionmaker(
                bind=schema_translated_engine,
                autoflush=False,
                autocommit=False,
                expire_on_commit=False,
            )
        )()
