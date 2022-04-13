from typing import Generator

import structlog

from billtitles.database import SessionLocal
from elasticsearch_dsl import connections


logger = structlog.getLogger()


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()  # noqa


def get_elasticsearch():
    try:
        yield get_es_connection()
    finally:
        pass
