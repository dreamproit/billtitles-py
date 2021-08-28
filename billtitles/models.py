from typing import Optional, List 
from datetime import datetime
from sqlmodel import Field, SQLModel

class Bill(SQLModel, table=True):
    __tablename__ = "bills"

    id: Optional[int] = Field(default=None, primary_key=True)
    billnumber: str = Field(index=True)

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

class BillToBill(SQLModel, table=True):
    __tablename__ = "bill_to_bills"

    id: Optional[int] = Field(default=None, primary_key=True)
    score: Optional[float] = Field(default=None)
    score_other: Optional[float] = Field(default=None)
    billnumber: str = Field(index=True)
    billnumber_to: str = Field(index=True)
    reason: str = Field(index=True)
    identified_by: str