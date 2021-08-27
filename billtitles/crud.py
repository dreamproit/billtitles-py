from sqlalchemy.orm import Session

from . import models, schemas


def get_bill(db: Session, bill_id: int):
    return db.query(models.Bill).filter(models.Bill.id == bill_id).first()


def get_bill_by_billnumber(db: Session, billnumber: str):
    return db.query(models.Bill).filter(models.Bill.billnumber == billnumber).first()


def get_bills(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Bill).offset(skip).limit(limit).all()


def create_bill(db: Session, bill: schemas.BillCreate):
    fake_hashed_password = bill.password + "notreallyhashed"
    db_bill = models.Bill(email=bill.email, hashed_password=fake_hashed_password)
    db.add(db_bill)
    db.commit()
    db.refresh(db_bill)
    return db_bill


def get_titles(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Title).offset(skip).limit(limit).all()


def create_bill_title(db: Session, title: schemas.TitleCreate, bill_id: int):
    db_title = models.Title(**title.dict(), owner_id=bill_id)
    db.add(db_title)
    db.commit()
    db.refresh(db_title)
    return db_title