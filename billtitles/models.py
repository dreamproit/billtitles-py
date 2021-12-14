from typing import Optional, List 
from datetime import datetime
from sqlmodel import Field, SQLModel
from .database import engine
from .pymodels import *

class Title(SQLModel, table=True):
    __tablename__ = "titles"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
class BillTitle(SQLModel, table=True):
    __tablename__ = "bill_titles"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    deleted_at: Optional[datetime] = Field(default=None)
    billnumber: str = Field(index=True)
    title: str = Field(index=True)
    is_for_whole_bill: bool = Field(default=False)

# For display
class BillTitlePlus(SQLModel, table=True):
    __tablename__ = "bill_titles_plus"

    id: Optional[int] = Field(default=None, primary_key=True)
    billnumber: str = Field(index=True)
    titles: str
    is_for_whole_bill: bool = Field(default=False)

class TitlesItem(SQLModel):
    whole: List[str]
    all: List[str]

class BillTitleResponse(SQLModel):
    billnumber: str 
    titles: TitlesItem

class TitleBillsResponseItem(SQLModel):
    id: int
    title: str 
    billnumbers: List[str] 

class TitleBillsResponse(SQLModel):
    titles: List[TitleBillsResponseItem]
    titles_whole: List[TitleBillsResponseItem]

class BillToBillPlus(BillToBillModel):
    title: str
    version: str
    version_to: str
    reasons: Optional[List[str]] = []

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

if __name__ == "__main__":
    create_db_and_tables()
