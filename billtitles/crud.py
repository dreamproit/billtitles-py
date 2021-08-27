from sqlalchemy.orm import Session
from sqlalchemy import func 

from . import models


def get_bill_by_billnumber(db: Session, billnumber: str = None):
    if not billnumber:
        return None
    billnumber=billnumber.strip("\"'")
    bills = db.query(models.BillTitle.billnumber, func.group_concat(models.BillTitle.title, "; ").label('titles') ).filter(models.BillTitle.billnumber == billnumber).filter(models.BillTitle.is_for_whole_bill == False).group_by(models.BillTitle.billnumber).all()
    bills_title_whole = db.query(models.BillTitle.billnumber, func.group_concat(models.BillTitle.title, "; ").label('titles') ).filter(models.BillTitle.billnumber == billnumber).filter(models.BillTitle.is_for_whole_bill == True).group_by(models.BillTitle.billnumber).all()
    return {"bills": bills, "bills_title_whole": bills_title_whole}

def get_bills(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.BillTitle.billnumber, models.BillTitle.title).offset(skip).limit(limit).all()

# TODO: document how to use this and whether it's working
# In particular, look at adding the titles 
#def create_bill(db: Session, bill: models.Bill):
#    db_bill = models.Bill(billnumber=bill.billnumber, billnumberversion=bill.billnumberversion, created_at=datetime.now(), updated_at=datetime.now())
#    db.add(db_bill)
#    db.commit()
#    db.refresh(db_bill)
#    return db_bill

def get_title(db: Session, title_id: int = None, title: str = None):
    # TODO: handle title_id

    if title_id:
        return db.query(models.BillTitle).filter(models.BillTitle.id == title_id).first()

    if title:
        title=title.strip("\"'")

    titles = db.query(models.BillTitle.title, func.group_concat(models.BillTitle.billnumber, "; ").label('bills') ).filter(models.BillTitle.title == title).filter(models.BillTitle.is_for_whole_bill == False).group_by(models.BillTitle.title).all()
    titles_whole = db.query(models.BillTitle.title, func.group_concat(models.BillTitle.billnumber, "; ").label('bills') ).filter(models.BillTitle.title == title).filter(models.BillTitle.is_for_whole_bill == True).group_by(models.BillTitle.title).all()
    return {'titles': titles, 'titles_whole': titles_whole} 

def get_titles(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.BillTitle.billnumber, models.BillTitle.title).offset(skip).limit(limit).all()