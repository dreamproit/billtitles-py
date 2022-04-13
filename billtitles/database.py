#!/usr/bin/env python3
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import create_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from billtitles.config import settings

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, echo=True)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=engine,
)

async_engine = create_async_engine(
    settings.SQLALCHEMY_ASYNC_DATABASE_URI,
    echo=True,
)
async_session = sessionmaker(
    async_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession,
)
