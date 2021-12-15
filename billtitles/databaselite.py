from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, create_engine
import models

sqlite_file_name = "../billtitles.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)

SessionLocalLite = sessionmaker(autocommit=False, autoflush=False, bind=engine)
