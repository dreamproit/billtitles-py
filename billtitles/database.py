#!/usr/bin/env python3

from sqlalchemy.orm import sessionmaker
from sqlmodel import create_engine

import constants

postgres_url = f"postgresql://postgres:{constants.POSTGRES_PW}@localhost/billsim"

engine = create_engine(postgres_url, echo=False)

SessionLocal = sessionmaker(autocommit=False,
                            autoflush=False,
                            expire_on_commit=False,
                            bind=engine)
