#!/usr/bin/env python3

from sqlalchemy.orm import sessionmaker
from sqlmodel import create_engine

from . import constants

#postgres_url = f"postgresql://postgres:{constants.POSTGRES_PW}@localhost/billsim"
if constants.POSTGRES_URL is None:
    postgres_url = f"postgresql://postgres:{constants.POSTGRES_PW}@localhost"
else:
    postgres_url = constants.POSTGRES_URL

engine = create_engine(postgres_url, echo=True)

SessionLocal = sessionmaker(autocommit=False,
                            autoflush=False,
                            expire_on_commit=False,
                            bind=engine)
