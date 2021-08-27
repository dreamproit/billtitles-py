from typing import Optional, List 
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship

class BillTitleLink(SQLModel, table=True):
    __tablename__ = "bill_titles"
    bill_id: Optional[int] = Field(
        default=None, foreign_key="bills.id", primary_key=True
    )
    title_id: Optional[int] = Field(
        default=None, foreign_key="titles.id", primary_key=True
    )

class BillWholeTitleLink(SQLModel, table=True):
    __tablename__ = "bill_titleswhole"
    bill_id: Optional[int] = Field(
        default=None, foreign_key="bills.id", primary_key=True
    )
    title_id: Optional[int] = Field(
        default=None, foreign_key="titles.id", primary_key=True
    )

# Create statement for bill titles table.
# CREATE TABLE `titles` (`id` integer,`created_at` datetime,`updated_at` datetime,`deleted_at` datetime,
# `title` text,PRIMARY KEY (`id`)) 
class Title(SQLModel, table=True):
    __tablename__ = "titles"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = Field(default=None)
    title: str = Field(index=True, default=None)
    bills: List["Bill"] = Relationship(back_populates="titles", link_model=BillTitleLink)

# Create statement from DBSQLite Browser
# CREATE TABLE `bills` (`id` integer,`created_at` datetime,`updated_at` datetime,`deleted_at` datetime,
# `billnumber` text NOT NULL,`billnumberversion` text,PRIMARY KEY (`id`))
class Bill(SQLModel, table=True):
    __tablename__ = "bills"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = Field(default=None)
    billnumber: str = Field(index=True, default=None)
    billnumberversion: str = Field(index=True, default=None)
    titles: List["Title"] = Relationship(back_populates="bills", link_model=BillTitleLink)
    titleswhole: List["Title"] = Relationship(back_populates="bills", link_model=BillWholeTitleLink)