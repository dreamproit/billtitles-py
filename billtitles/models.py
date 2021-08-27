from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import PrimaryKeyConstraint, ForeignKeyConstraint, Table
from sqlalchemy.sql.sqltypes import DateTime

from .database import Base

bill_titles = Table('bill_titles',
    Base.metadata,
    Column('title_id', Integer, ForeignKey('titles.id'), primary_key=True),
    Column('bill_id', Integer, ForeignKey('bills.id'), primary_key=True)
)

bill_titleswhole = Table('bill_titleswhole',
    Base.metadata,
    Column('title_id', Integer, ForeignKey('titles.id'), primary_key=True),
    Column('bill_id', Integer, ForeignKey('bills.id'), primary_key=True)
)

# Create statement for bill titles table.
# CREATE TABLE `titles` (`id` integer,`created_at` datetime,`updated_at` datetime,`deleted_at` datetime,
# `title` text,PRIMARY KEY (`id`)) 
class Title(Base):
    __tablename__ = "titles"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    deleted_at = Column(DateTime)
    title = Column(String(255), unique=True, nullable=False)
    bills = relationship("Bill", secondary="bill_titles", back_populates="titles",)

# Create statement from DBSQLite Browser
# CREATE TABLE `bills` (`id` integer,`created_at` datetime,`updated_at` datetime,`deleted_at` datetime,
# `billnumber` text NOT NULL,`billnumberversion` text,PRIMARY KEY (`id`))
class Bill(Base):
    __tablename__ = "bills"


    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    deleted_at = Column(DateTime)
    billnumber = Column(String(255), unique=True, nullable=False)
    billnumberversion = Column(String(255))
    titles = relationship("Title", secondary="bill_titles", back_populates="bills",)
    titleswhole = relationship("Title", secondary="bill_titleswhole", back_populates="bills",)