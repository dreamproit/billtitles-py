from datetime import datetime
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func

from . import models
from typing import TypedDict


def deep_get(d, keys, default=None):
    """
    Example:
        d = {'meta': {'status': 'OK', 'status_code': 200}}
        deep_get(d, ['meta', 'status_code'])          # => 200
        deep_get(d, ['garbage', 'status_code'])       # => None
        deep_get(d, ['meta', 'garbage'], default='-') # => '-'
    """
    assert type(keys) is list
    if d is None:
        return default
    if not keys:
        return d
    return deep_get(d.get(keys[0]), keys[1:], default)
class BillsResponse(TypedDict):
    bills: List[models.BillTitlePlus] 
    bills_title_whole: List[models.BillTitlePlus] 

def get_bill_titles_by_billnumber(db: Session, billnumber: str = None):
    if not billnumber:
        return None
    billnumber=billnumber.strip("\"'").lower()
    # In postgres it may be possible to use array_agg like this: 
    # titles_main_resp = db.query(models.BillTitle.billnumber, func.array_agg(models.BillTitle.title).label('titles_main') ).filter(models.BillTitle.billnumber == billnumber).filter(models.BillTitle.is_for_whole_bill == True).group_by(models.BillTitle.billnumber).all()
    titles_whole_resp = db.query(models.BillTitle.billnumber, func.group_concat(models.BillTitle.title, "; ").label('titles') ).filter(models.BillTitle.billnumber == billnumber).filter(models.BillTitle.is_for_whole_bill == True).group_by(models.BillTitle.billnumber).all()
    titles_all_resp = db.query(models.BillTitle.billnumber, func.group_concat(models.BillTitle.title, "; ").label('titles') ).filter(models.BillTitle.billnumber == billnumber).filter(models.BillTitle.is_for_whole_bill == False).group_by(models.BillTitle.billnumber).all()
    if len(titles_whole_resp) > 0:
        titles_whole = titles_whole_resp[0].titles.split('; ')
    else:
        titles_whole = []
    if len(titles_all_resp) > 0:
        titles_all = titles_all_resp[0].titles.split('; ')
    else:
        titles_all = []
    return models.BillTitleResponse(billnumber= billnumber, titles= models.TitlesItem(whole=titles_whole, all= titles_all))

def get_related_bills(db: Session, billnumber: str = None):
    if not billnumber:
        return None
    billnumber=billnumber.strip("\"'").lower()
    bills = db.query(models.BillToBill, models.Bill).filter(models.Bill.billnumber == billnumber).all()
    return bills 

def get_related_bills_w_titles(db: Session, billnumber: str = None) -> List[models.BillToBillModel]: 
    if not billnumber:
        return [] 
    billnumber=billnumber.strip("\"'").lower()
    bills = db.query(models.BillToBill, models.Bill).filter(models.Bill.billnumber == billnumber).all()
    newbills = []
    for bill in bills:
        billplus = models.BillToBillModel(**bill.__dict__)
        billtitles = dict(get_title_by_billnumber(db, bill.billnumber_to))
        if len(billtitles.get('titles_whole', [])) > 0:
            billplus.title = billtitles.get('titles_whole', [])[0]['titles'].split('; ')[0]
        if billplus.reason and len(billplus.reason) > 0:
            billplus.reasons = billplus.reason.split('; ')
        newbills.append(billplus)
    return sorted(newbills, key=lambda k: k.score if k.score is not None else 0, reverse=True)

def create_billtobill(db: Session, billtobill: models.BillToBill):
    db.add(billtobill)
    db.commit()
    db.refresh(billtobill)
    return billtobill 

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

def get_title_by_id(db: Session, title_id: int):
    return db.query(models.BillTitle).filter(models.BillTitle.title_id == title_id).first()

def get_title(db: Session, title: str) -> models.TitleBillsResponse:

    title=title.strip("\"'")

    titles = [models.TitleBillsResponseItem(id=item.id, title=item.title, billnumbers=item.billnumbers.split('; ')) for item in db.query(models.Bill.billnumber, models.Title.title, models.BillTitle.title_id, func.group_concat(models.Bill.billnumber, "; ").label('billnumbers') ).filter(models.Title.title == title).filter(models.BillTitle.is_for_whole_bill == False).group_by(models.Title.title).all()]
    titles_whole = [models.TitleBillsResponseItem(id=item.id, title=item.title, billnumbers=item.billnumbers.split('; ')) for item in db.query(models.Bill.billnumber, models.Title.title, models.BillTitle.title_id, func.group_concat(models.Bill.billnumber, "; ").label('billnumbers') ).filter(models.Title.title == title).filter(models.BillTitle.is_for_whole_bill == True).group_by(models.Title.title).all()]
    return models.TitleBillsResponse(titles=titles, titles_whole= titles_whole) 

def get_titles(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Bill.billnumber, models.Title.title).offset(skip).limit(limit).all()

def get_title_by_billnumber(db: Session, billnumber: str = None):
    if not billnumber:
        return {"titles": [], "titles_whole": []}
    billnumber=billnumber.strip("\"'").lower()
    titles = db.query(models.Bill.billnumber, func.group_concat(models.Title.title, "; ").label('titles') ).filter(models.Bill.billnumber == billnumber).filter(models.BillTitle.is_for_whole_bill == False).group_by(models.Bill.billnumber).all()
    titles_whole = db.query(models.Bill.billnumber, func.group_concat(models.Title.title, "; ").label('titles') ).filter(models.Bill.billnumber == billnumber).filter(models.BillTitle.is_for_whole_bill == True).group_by(models.Bill.billnumber).all()
    return {"titles": titles, "titles_whole": titles_whole}

def get_billtitle(db: Session, title: str, billnumber: str):
    return db.query(models.Bill.billnumber, models.Title.title).filter_by(title=title, billnumber=billnumber).first()

def add_title(db: Session, title: str, billnumbers: List[str], is_for_whole_bill: bool = False):
    if title:
        title=title.strip("\"'")
    created_at = datetime.now()
    updated_at = datetime.now()
    newTitle = models.Title(title=title)
    db.add(newTitle) 
    db.commit()
    msg = ""
    for billnumber in billnumbers:
        billtitle = get_billtitle(db, title, billnumber)
        if billtitle:
            newmsg = "Title already exists: '" + title + "' for bill: " + billnumber
            msg = newmsg + "; " + msg
            continue

        created_at = datetime.now()
        updated_at = datetime.now()
        newBillTitle = models.BillTitle(title=title, created_at=created_at, updated_at=updated_at, billnumber=billnumber, is_for_whole_bill=is_for_whole_bill)
        db.add(newBillTitle) 
        db.commit()
        msg = "Title added: '" + title + "' for bill: " + billnumber + "; " + msg
    return {"billtitle": newTitle, "message": msg}

# Removes the title entry, with all bills associated with it
def remove_title(db: Session, title: str):
    rows = db.query(models.Title).filter_by(title=title).delete()
    # TODO: check if this deletes the join table entries too
    db.commit()
    if rows >0:
        return {"title": title, "message": "Title removed"}
    else:
        return {"title": title, "message": "Title not found"}