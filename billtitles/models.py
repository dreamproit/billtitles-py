#!/usr/bin/env python3

from typing import Optional

from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy.sql.sqltypes import VARCHAR
from sqlmodel import Field, SQLModel, Column

from .database import engine


class Bill(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("billnumber", "version", name="billnumber_version"),
    )
    id: Optional[int] = Field(default=None, primary_key=True)
    length: Optional[int] = None
    # TODO: when indexing/storing Bill initially, calculate number of sections
    # sections_num: Optional[int] = None
    billnumber: str = Field(index=True)
    version: str = Field(index=True)

    @classmethod
    def getBillnumberversion(cls):
        return "{cls.billnumber}{cls.version}".format(cls=cls)


# Model used to store in db
class BillToBill(SQLModel, table=True):
    bill_id: Optional[int] = Field(
        default=None, foreign_key="bill.id", primary_key=True
    )
    bill_to_id: Optional[int] = Field(
        default=None, foreign_key="bill.id", primary_key=True
    )
    score_es: Optional[float] = None
    score: Optional[float] = None
    score_to: Optional[float] = None
    reasonsstring: Optional[str] = Field(default=None, sa_column=Column(VARCHAR(100)))
    identified_by: Optional[str] = None
    sections_num: Optional[int] = None
    sections_match: Optional[int] = None


# NOTE: section_id is the id attribute from the XML. It may not be unique.
# However, the SQL bill_id + section_id is unique.
class SectionItem(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("bill_id", "section_id", name="billnumber_version_section_id"),
    )
    id: Optional[int] = Field(default=None, primary_key=True)
    bill_id: Optional[int] = Field(default=None, foreign_key="bill.id")
    section_id: Optional[str] = Field(default=None)
    label: Optional[str] = Field(default=None, index=True)
    header: Optional[str] = Field(default=None, index=True)
    length: int


class SectionToSection(SQLModel, table=True):
    """
    This is a self-join of the SectionItem table.
    """

    id: Optional[int] = Field(
        default=None, foreign_key="sectionitem.id", primary_key=True
    )
    id_to: Optional[int] = Field(
        default=None, foreign_key="sectionitem.id", primary_key=True
    )
    score_es: Optional[float] = None
    score: Optional[float] = None
    score_to: Optional[float] = None


# From billtitles-py
class Title(SQLModel, table=True):
    __tablename__ = "titles"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)


class BillTitle(SQLModel, table=True):
    __tablename__ = "bill_titles"

    title_id: Optional[int] = Field(
        default=None, foreign_key="titles.id", primary_key=True
    )
    bill_id: Optional[int] = Field(
        default=None, foreign_key="bill.id", primary_key=True
    )
    is_for_whole_bill: bool = Field(default=False)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


if __name__ == "__main__":
    create_db_and_tables()
