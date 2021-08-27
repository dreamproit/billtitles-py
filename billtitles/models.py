from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import PrimaryKeyConstraint, ForeignKeyConstraint
from sqlalchemy.sql.sqltypes import DateTime

from .database import Base

#CREATE TABLE `bill_titles` (`title_id` integer,`bill_id` integer,PRIMARY KEY (`title_id`,`bill_id`),
# CONSTRAINT `fk_bill_titles_title` FOREIGN KEY (`title_id`) REFERENCES `titles`(`id`),CONSTRAINT `fk_bill_titles_bill` FOREIGN KEY (`bill_id`) REFERENCES `bills`(`id`)) 
class BillTitle(Base):

    __tablename__ = 'bill_titles'
    title_id = Column(Integer, ForeignKey('titles.id'), nullable=False)
    bill_id = Column(Integer, ForeignKey('bills.id'), nullable=False)
    titles = Column(Integer, nullable=False)
    bills = Column(Integer, nullable=False)
    __table_args__ = (
        PrimaryKeyConstraint(title_id, bill_id),
        {},
    )

#CREATE TABLE `bill_titleswhole` (`bill_id` integer,`title_id` integer,PRIMARY KEY (`bill_id`,`title_id`),
# CONSTRAINT `fk_bill_titleswhole_bill` FOREIGN KEY (`bill_id`) REFERENCES `bills`(`id`),CONSTRAINT `fk_bill_titleswhole_title` FOREIGN KEY (`title_id`) REFERENCES `titles`(`id`))
class BillTitleWhole(Base):
    __tablename__ = 'bill_titleswhole'
    title_id = Column(Integer, ForeignKey('titles.id'), nullable=False)
    bill_id = Column(Integer, ForeignKey('bills.id'), nullable=False)
    titles = Column(Integer, nullable=False)
    bills = Column(Integer, nullable=False)
    __table_args__ = (
        PrimaryKeyConstraint(title_id, bill_id),
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
    bills = relationship('Title', secondary='bill_titles', backref='titles', primaryjoin="Title.id == BillTitle.title_id", secondaryjoin="Bill.id == BillTitle.bill_id")

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
    titles = relationship('Bill', secondary='bill_titles', backref='Bill', primaryjoin="Bill.id == BillTitle.bill_id", secondaryjoin="Titles.id == BillTitle.title_id")
    titleswhole = relationship('Bill', secondary='bill_titleswhole', backref='bills', primaryjoin="Bill.id == BillTitlewhole.bill_id", secondaryjoin="Titles.id == BillTitlewhole.title_id")