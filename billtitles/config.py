import secrets
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import structlog
from pydantic import (
    AnyHttpUrl,
    BaseSettings,
    EmailStr,
    HttpUrl,
    PostgresDsn,
    validator,
    AnyUrl,
)
from structlog import make_filtering_bound_logger
from typing_extensions import Literal


class AsyncPostgresDsn(AnyUrl):
    allowed_schemes = {"postgres", "postgresql", "postgresql+asyncpg"}
    user_required = True


LogLevelEnum = Enum(
    "LogLevelEnum", {k: k for k in structlog._log_levels._NAME_TO_LEVEL}
)


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    # absolute data dir path
    DATA_DIR: Path = Path("/congress/data")
    # SECRET_KEY: str = secrets.token_urlsafe(32)

    LOG_LEVEL: LogLevelEnum = "info"

    SENTRY_DSN: Optional[HttpUrl] = None

    @validator("SENTRY_DSN", pre=True)
    def sentry_dsn_can_be_blank(cls, v: str) -> Optional[str]:
        if not v or len(v) == 0:
            return None
        return v

    POSTGRES_HOST: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_PORT: int
    POSTGRES_DB: str

    SQLALCHEMY_DATABASE_URI: Optional[AsyncPostgresDsn] = None
    SQLALCHEMY_POOL_SIZE: int = 15
    SQLALCHEMY_POOL_MAX_OVERFLOW: int = 5

    SQLALCHEMY_ASYNC_DATABASE_URI: Optional[AsyncPostgresDsn] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_sqlalchemy_database_uri(
        cls, v: Optional[str], values: Dict[str, Any]
    ) -> Optional[str]:
        return cls.assemble_db_connection(v, values)

    @validator("SQLALCHEMY_ASYNC_DATABASE_URI", pre=True)
    def assemble_sqlalchemy_async_database_uri(
        cls, v: Optional[str], values: Dict[str, Any]
    ) -> Optional[str]:
        return cls.assemble_db_connection(v, values, True)

    @classmethod
    def assemble_db_connection(
        cls, v: Optional[str], values: Dict[str, Any], is_async: bool = False
    ) -> Any:
        if isinstance(v, str):
            return v
        return AsyncPostgresDsn.build(
            scheme="postgresql" if not is_async else "postgresql+asyncpg",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_HOST"),
            port=str(values.get("POSTGRES_PORT")) or "5432",
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    # MESSAGE_BROKER_URI: str

    BACKEND_SENTRY_ENABLED: bool = True
    ELASTICSEARCH_URI: Optional[str]

    class Config:
        case_sensitive = True


settings = Settings()
structlog.configure(
    wrapper_class=make_filtering_bound_logger(
        structlog._log_levels._NAME_TO_LEVEL.get(settings.LOG_LEVEL, 20)
    )
)
