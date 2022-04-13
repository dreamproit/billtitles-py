#!/usr/bin/env python3

import datetime
from typing import Optional
import enum

from sqlalchemy import UniqueConstraint, orm, not_
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql.sqltypes import VARCHAR
from sqlmodel import Column
from sqlmodel import SQLModel, Field, Relationship, Enum

from .database import engine


# This is the basis for making queries, using billsim.bill_similarity.py getSimilarSectionItem
# Result of the similarity search, collecting top similar sections for each section of the bill


class BillBasic(SQLModel, table=True):
    """
    ### Bill Basic Information Model
    """

    __tablename__ = "btiapp_billbasic"
    __table_args__ = (UniqueConstraint("bill_number"),)

    # BILL_TYPE_CHOICES = (
    #     ("hr", "H.R. 1234"),  # It stands for House of Representatives,
    #     # but it is the prefix used for bills introduced in the House.
    #     ("hres", "H.Res. 1234"),  # It stands for House Simple Resolution.
    #     ("hconres", "H.Con.Res. 1234"),  # It stands for House Concurrent Resolution.
    #     ("hjres", "H.J.Res. 1234"),  # It stands for House Joint Resolution.
    #     ("s", "S. 1234"),  # It stands for Senate and it is the prefix used for bills
    #     # introduced in the Senate.  Any abbreviation besides "S." is incorrect.
    #     ("sres", "S.Res. 1234"),  # It stands for Senate Simple Resolution.
    #     ("sconres", "S.Con.Res. 1234"),  # It stands for Senate Concurrent Resolution.
    #     ("sjres", "S.J.Res. 1234"),  # It stands for Senate Joint Resolution.
    # )
    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    # [bill_type][number]-[congress]
    bill_id: str = Field(max_length=20)

    # Bill_type can be one of hr, hres, hjres, hconres, s, sres, sjres, sconres.
    # These are distinct sorts of legislative documents.
    # Two of these(hr, s) are for bills. The remaining are types of resolutions.
    # It is important that when you display these types that
    # you use the standard abbreviations.
    #
    # Simple resolutions only get a vote in their originating chamber.
    # Concurrent resolutions get a vote in both chambers but do not
    # go to the President.
    # Neither has the force of law.
    # Joint resolutions can be used either to propose an amendment to the
    # constitution or to propose a law.
    # When used to propose a law, they have exactly the same procedural steps as bills.
    bill_type: str = Field(
        max_length=10,
        # choices=BILL_TYPE_CHOICES,
    )

    # The bill number is a positive integer.
    # Bills die at the end of a Congress and numbering starts with
    # 1 at the beginning of each new Congress.
    number: int = Field()
    # [congress][bill_type][number]
    bill_number: str = Field(max_length=20)
    congress: int = Field()
    introduced_at: datetime.date = Field(
        # auto_now=False,
        # auto_now_add=False,
    )
    updated_at: datetime.datetime = Field(
        default_factory=datetime.datetime.now,
    )

    # bill_titles: "BillTitle" = Relationship(
    #     # sa_relationship_kwargs=dict(
    #     #     # secondary=BillTitles.__table__,
    #     #     primaryjoin="foreign(BillBasic.bill_number) == Bill.billnumber"
    #     # )
    # )


class BillTitles(SQLModel, table=True):
    """
    ### Bill Titles Model

    Bills can have "official" descriptive titles (almost always),
    "short" catchy titles (sometimes), and "popular" nickname titles (rare).
    They can have many of these titles, given at various stages of a bill's life.
    The current official, short, and popular titles are kept in top-level
    official_title, short_title, and popular_title fields.

    Popular titles are assigned by the Library of Congress,
    and can be added at any time.
    """

    __tablename__ = "btiapp_billtitles"

    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    bill_basic_id: int = Field(foreign_key="btiapp_billbasic.id")
    bill_basic: "BillBasic" = Relationship()
    # bill_basic = models.OneToOneField(
    #     BillBasic,
    #     verbose_name=_("bill_basic"),
    #     related_name="billtitles",
    #     on_delete=models.CASCADE,
    # )
    official_title: Optional[str] = Field(
        max_length=2000,
        default=None,
    )
    popular_title: Optional[str] = Field(
        max_length=2000,
        default=None,
    )
    short_title: Optional[str] = Field(
        max_length=2000,
        default=None,
    )


class BillStageTitle(SQLModel, table=True):
    """
    ### Bill Status XML Title Model

    A bill may have multiple titles for any given stage.
    `is_for_portion` is `true` when the title is for a portion of the bill,
    and these titles should not be used when choosing a title
    for display for the entire bill.
    """

    __tablename__ = "btiapp_billstagetitle"

    # TITLE_TYPE_CHOICES = (
    #     ("O", "official"),
    #     ("P", "popular"),
    #     ("S", "short"),
    # )
    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    bill_basic_id: int = Field(foreign_key="btiapp_billbasic.id")
    bill_basic: BillBasic = Relationship()
    #     models.ForeignKey(
    #     BillBasic,
    #     verbose_name=_("bill_basic"),
    #     related_name="billstagetitle",
    #     on_delete=models.CASCADE,
    # )
    title: str = Field(max_length=2000)
    titleNoYear: str = Field(max_length=2000)
    type: Optional[str] = Field(
        max_length=10,
        # choices=TITLE_TYPE_CHOICES,
        default=None,
    )
    As: Optional[str] = Field(
        max_length=50,
        default=None,
    )
    is_for_portion: Optional[bool] = Field(default=None)


class Bill(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("billnumber", "version", name="billnumber_version"),
    )
    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    length: Optional[int] = None
    # TODO: when indexing/storing Bill initially, calculate number of sections
    # sections_num: Optional[int] = None
    billnumber: str = Field(
        index=True,
        # TODO: when data is loaded and migrated, add foreignkey.
        # foreign_key="btiapp_billbasic.bill_number",
    )
    version: str = Field(index=True)

    basic_bill: BillBasic = Relationship(
        sa_relationship_kwargs=dict(
            primaryjoin="foreign(BillBasic.bill_number) == Bill.billnumber"
        )
    )

    def getBillnumberversion(cls):
        return "{cls.billnumber}{cls.version}".format(cls=cls)


# Model used to store in db
class BillToBill(SQLModel, table=True):
    bill_id: Optional[int] = Field(
        default=None, foreign_key="bill.id", primary_key=True, nullable=False
    )
    bill_to_id: Optional[int] = Field(
        default=None, foreign_key="bill.id", primary_key=True, nullable=False
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
    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
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
        default=None, foreign_key="sectionitem.id", primary_key=True, nullable=False
    )
    id_to: Optional[int] = Field(
        default=None, foreign_key="sectionitem.id", primary_key=True, nullable=False
    )
    score_es: Optional[float] = None
    score: Optional[float] = None
    score_to: Optional[float] = None


# From billtitles-py
class Title(SQLModel, table=True):
    __tablename__ = "titles"

    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    title: str = Field(index=True)


class TitleType(enum.Enum):
    official = "official"
    popular = "popular"
    short = "short"


class BillTitle(SQLModel, table=True):
    """Represents a title of a bill.
    is_for_whole_bill: True if the title is for the whole bill.
    type: official, popular, short
    is_for_portion: True if the title is for a portion of the bill.
    As: one of the following: {
        agreed to by house and senate
        amended by house
        amended by senate
        conference report
        enacted
        introduced
        passed house
        passed senate
        reported to house
        reported to senate
    }
    """

    __tablename__ = "bill_titles"

    title_id: Optional[int] = Field(
        default=None, foreign_key="titles.id", primary_key=True, nullable=False
    )
    bill_id: Optional[int] = Field(
        default=None, foreign_key="bill.id", primary_key=True, nullable=False
    )
    is_for_whole_bill: bool = Field(default=False)

    type: TitleType = Field(nullable=False, sa_column=Column(Enum(TitleType)))
    As: Optional[str] = Field(max_length=50, default=None)

    # @hybrid_property
    # def is_for_portion(self):
    #     return not self.is_for_whole_bill
    #
    # @is_for_portion.expression
    # def is_for_portion(cls):
    #     return not_(cls.is_for_whole_bill)
    #
    # class Config:
    #     arbitrary_types_allowed = True


#     __mapper_args__ = {
#         "polymorphic_identity": "title",
#         "polymorphic_on": "type",
#     }
#
#
# class ShortTitle(BillTitle):
#     __mapper_args__ = {
#         "polymorphic_identity": TitleType.short,
#     }
#
#
# class PopularTitle(BillTitle):
#     __mapper_args__ = {
#         "polymorphic_identity": TitleType.popular.value,
#     }
#
#
# class OfficialTitle(BillTitle):
#     __mapper_args__ = {
#         "polymorphic_identity": TitleType.official.value,
#     }
#

# For display (from billtitles-py)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


if __name__ == "__main__":
    create_db_and_tables()
