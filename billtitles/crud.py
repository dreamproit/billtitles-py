from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import aliased, Session
from sqlalchemy import func, desc
from sqlalchemy.sql.elements import literal_column

from . import models
from typing import TypedDict

bill_to = aliased(models.Bill)


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
    titles_whole_resp = db.query(models.Bill, func.string_agg(models.Title.title, literal_column("'; '")).label('titles')).filter(models.Bill.billnumber==billnumber).join(models.BillTitle, models.BillTitle.bill_id == models.Bill.id).join(models.Title, models.Title.id == models.BillTitle.title_id).filter(models.BillTitle.is_for_whole_bill == True).group_by(models.Bill.id).all()
    titles_all_resp = db.query(models.Bill, func.string_agg(models.Title.title, literal_column("'; '")).label('titles')).filter(models.Bill.billnumber==billnumber).join(models.BillTitle, models.BillTitle.bill_id == models.Bill.id).join(models.Title, models.Title.id == models.BillTitle.title_id).group_by(models.Bill.id).all()
    if len(titles_whole_resp) > 0:
        titles_whole = titles_whole_resp[0].titles.split('; ')
    else:
        titles_whole = []
    if len(titles_all_resp) > 0:
        titles_all = titles_all_resp[0].titles.split('; ')
    else:
        titles_all = []
    return models.BillTitleResponse(billnumber= billnumber, titles= models.TitlesItem(whole=titles_whole, all= titles_all))

def get_related_bills(db: Session, billnumber: str = None, version: str = None, withTitle: bool = True, flat: Optional[bool] = True, billsonly: Optional[bool] = False) -> List[models.BillToBillModel or models.BillToBillModelDeep]:
    if not billnumber:
        return [] 
    billnumber=billnumber.strip("\"'").lower()
    if version:
        version=version.strip("\"'").lower()
    if not version:
        subquery = db.query(models.Bill.billnumber, models.Bill.version, models.Bill.length,
                            models.BillToBill.score, models.BillToBill.score_to, models.BillToBill.reasonsstring,
                            models.BillToBill.sections_num, models.BillToBill.sections_match, models.BillToBill.score_es, 
                            models.BillToBill.bill_id, models.BillToBill.bill_to_id
                            ).filter(models.Bill.billnumber == billnumber).join(models.BillToBill, models.BillToBill.bill_id == models.Bill.id).subquery();
        bills = db.query(bill_to.billnumber.label("billnumber_to"), bill_to.version.label("version_to"), bill_to.length.label("length_to"), subquery).filter(subquery.c.bill_to_id == bill_to.id).order_by(desc(subquery.c.score)).all()
    else:
        subquery = db.query(models.Bill.billnumber, models.Bill.version, models.Bill.length,
                            models.BillToBill.score, models.BillToBill.score_to, models.BillToBill.reasonsstring,
                            models.BillToBill.sections_num, models.BillToBill.sections_match, models.BillToBill.score_es,
                            models.BillToBill.bill_id, models.BillToBill.bill_to_id
                            ).filter(models.Bill.billnumber == billnumber, models.Bill.version == version).join(models.BillToBill, models.BillToBill.bill_id == models.Bill.id).subquery();
        bills = db.query(bill_to.billnumber.label("billnumber_to"), bill_to.version.label("version_to"), bill_to.length.label("length_to"), subquery).filter(subquery.c.bill_to_id == bill_to.id).order_by(desc(subquery.c.score)).all()
        
    billdicts = []
    titles = get_bill_titles_by_billnumber(db, billnumber)
    title = None
    if titles:
        if titles.titles.whole:
            title = titles.titles.whole[0]
        else:
            if titles.titles.all:
                title = titles.titles.all[0]
    for bill in bills:
        bill = bill._asdict()
        bill['billnumber_version'] = bill.get('billnumber', '') + bill.get('version', '')
        bill['length_to'] = bill.get('length_to', 0)
        bill['billnumber_version_to'] = bill.get('billnumber_to', '') + bill.get('version_to', '')
        bill['reasons'] = bill.get('reasonsstring', '').split(', ')
        if withTitle:
            titles_to = get_bill_titles_by_billnumber(db, bill.get('billnumber_to'))
            #titles = get_titles_by_bill_id(db, bill.get('bill_id'))
            bill['titles_to'] = titles_to
            title_to = None
            if titles_to:
                if titles_to.titles.whole:
                    title_to = titles_to.titles.whole[0]
                else:
                    if titles_to.titles.all:
                        title_to = titles_to.titles.all[0]
            bill['title_to'] = title_to
            bill['titles_to'] = titles_to
            bill['titles'] = titles
            bill['title'] = title
        billdicts.append(bill)
    if billsonly:
       billsList = [bill['billnumber_version_to'] for bill in billdicts] 
       return billsList
    if flat == False:
        extrafields = ['reasons', 'score', 'score_to', 'identified_by', 'sections_num', 'sections_match', 'sections']
        billdicts_to = []
        billfrom = None
        for billdict in billdicts:
            billdict_deep_extra = { 'reasons': billdict.get('reasons', []), 
              'score': billdict.get('score', 0), 
              'score_to': billdict.get('score_to', 0), 
              'identified_by': billdict.get('identified_by', None),
              'sections_num': billdict.get('sections_num', None),
              'sections_match': billdict.get('sections_match', None),
              'sections': billdict.get('sections', None)}  
            billdict_deep_to = models.BillModelDeep(**{keyitem.replace("_to", ""): billdict[keyitem] for keyitem in billdict.keys() if keyitem.find('_to') > -1 and keyitem not in extrafields}, **billdict_deep_extra)
            billdicts_to.append(billdict_deep_to)
        # TODO add the 'from' bill at the beginning of the list
        #billfrom = {'bill': models.BillModelDeep(**{keyitem: billdicts[0][keyitem] for keyitem in billdicts.keys() if not keyitem.find('_to') > -1 and keyitem not in extrafields})}
        return billdicts_to
    return billdicts

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

    titles = [models.TitleBillsResponseItem(id=item.id, title=item.title, billnumbers=item.billnumbers.split('; ')) for item in db.query(models.Bill.billnumber, models.Title.title, models.BillTitle.title_id, func.group_concat(models.Bill.billnumber, "; ").label('billnumbers') ).filter(models.Title.title == title).group_by(models.Title.title).all()]
    titles_whole = [models.TitleBillsResponseItem(id=item.id, title=item.title, billnumbers=item.billnumbers.split('; ')) for item in db.query(models.Bill.billnumber, models.Title.title, models.BillTitle.title_id, func.group_concat(models.Bill.billnumber, "; ").label('billnumbers') ).filter(models.Title.title == title).filter(models.BillTitle.is_for_whole_bill == True).group_by(models.Title.title).all()]
    return models.TitleBillsResponse(titles=titles, titles_whole= titles_whole) 

def get_titles(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Bill.billnumber, models.Title.title).offset(skip).limit(limit).all()

def get_titles_by_bill_id(db: Session, bill_id: int):
    return db.query(models.BillTitle, models.Title.title).filter(models.BillTitle.bill_id == bill_id).join(models.Title,
                                                                                        models.Title.id == models.BillTitle.title_id).all()

def get_title_by_billnumber(db: Session, billnumber: str = None):
    if not billnumber:
        return {"titles": [], "titles_whole": []}
    billnumber=billnumber.strip("\"'").lower()
    titles = db.query(models.Bill.billnumber, func.group_concat(models.Title.title, "; ").label('titles') ).filter(models.Bill.billnumber == billnumber).group_by(models.Bill.billnumber).all()
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