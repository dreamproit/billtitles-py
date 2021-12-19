#!/usr/bin/env python3

from sqlalchemy.orm import sessionmaker
from sqlmodel import create_engine

from . import constants

#postgres_url = f"postgresql://postgres:{constants.POSTGRES_PW}@localhost/billsim"
postgres_url = f"postgresql://postgres:{constants.POSTGRES_PW}@localhost"

engine = create_engine(postgres_url, echo=True)

SessionLocal = sessionmaker(autocommit=False,
                            autoflush=False,
                            expire_on_commit=False,
                            bind=engine)
