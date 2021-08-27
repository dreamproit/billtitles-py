from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import PrimaryKeyConstraint
from sqlalchemy.sql.sqltypes import DateTime

from .database import Base

#CREATE TABLE `bill_titles` (`title_id` integer,`bill_id` integer,PRIMARY KEY (`title_id`,`bill_id`),CONSTRAINT `fk_bill_titles_title` FOREIGN KEY (`title_id`) REFERENCES `titles`(`id`),CONSTRAINT `fk_bill_titles_bill` FOREIGN KEY (`bill_id`) REFERENCES `bills`(`id`)) 
class BillTitle(Base):

    __tablename__ = 'bill_titles'
    titleId = Column('title_id', Integer)
    billId = Column('bill_id', Integer)
    __table_args__ = (
        PrimaryKeyConstraint(titleId, billId),
        {},
    )

class BillTitleWhole(Base):
    __tablename__ = 'bill_titleswhole'
    titleId = Column('title_id', Integer)
    billId = Column('bill_id', Integer)
    __table_args__ = (
        PrimaryKeyConstraint(titleId, billId),
        {},
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
    bills = relationship('bill', secondary=BillTitle, backref='Title')

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
    titles = relationship('bill', secondary=BillTitle, backref='Bill')
    titleswhole = relationship('bill', secondary=BillTitleWhole, backref='Bill')