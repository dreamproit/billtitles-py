from sqlalchemy.orm import Session
from datetime import datetime

from . import models


def get_bill(db: Session, bill_id: int):
    #return db.query(models.Bill).filter(models.Bill.id == bill_id).first()
    return db.query(models.Bill.id, models.Bill.billnumber, models.Bill.billnumberversion, models.Title.id, models.Title.title, models.BillTitleLink.bill_id, models.BillTitleLink.title_id).select_from(models.Bill).join(models.BillTitleLink).join(models.Title).filter(models.Bill.id == bill_id).first()

# TODO: get bill by billnumberversion
def get_bill_by_billnumber(db: Session, billnumber: str):
    #return db.query(models.Bill).filter(models.Bill.billnumber == billnumber).join(models.BillTitleLink).join(models.Title).all()
    return db.query(models.Bill.id, models.Bill.billnumber, models.Bill.billnumberversion, models.Title.title ).select_from(models.Bill).join(models.BillTitleLink).join(models.Title).filter(models.Bill.billnumber == billnumber).all()

def get_bills(db: Session, skip: int = 0, limit: int = 100):
    #return db.query(models.Bill).offset(skip).limit(limit).all()
    return db.query(models.Bill.id, models.Bill.billnumber, models.Bill.billnumberversion, models.Title.title ).select_from(models.Bill).join(models.BillTitleLink).join(models.Title).offset(skip).limit(limit).all()


# TODO: document how to use this and whether it's working
# In particular, look at adding the titles 
def create_bill(db: Session, bill: models.Bill):
    db_bill = models.Bill(billnumber=bill.billnumber, billnumberversion=bill.billnumberversion, created_at=datetime.now(), updated_at=datetime.now())
    db.add(db_bill)
    db.commit()
    db.refresh(db_bill)
    return db_bill


def get_title(db: Session, title_id: int):
    return db.query(models.Title).filter(models.Title.id == title_id).first()

def get_titles(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Title).offset(skip).limit(limit).all()

# TODO: document how to use this and whether it's working
# In particular, look at adding the bills
def create_bill_title(db: Session, title: models.Title):
    db_title = models.Title(**title.dict())
    db.add(db_title)
    db.commit()
    db.refresh(db_title)
    return db_title