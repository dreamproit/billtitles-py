from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from sqlmodel import SQLModel

from . import crud, models
from .database import SessionLocal, engine

SQLModel.metadata.create_all(engine)

# Run in uvicorn with:
# uvicorn billtitles.main:app --reload
app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/bills/", response_model=models.Bill)
def create_bill(bill: models.Bill, db: Session = Depends(get_db)):
    db_bill = crud.get_bill_by_billnumber(db, billnumber=bill.billnumber)
    if db_bill:
        raise HTTPException(status_code=400, detail="Billnumber already registered")
    return crud.create_bill(db=db, bill=bill)


@app.get("/bills/", response_model=List[models.BillAndTitle])
def read_bills(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    bills = crud.get_bills(db, skip=skip, limit=limit)
    return bills


# TODO: The current database does not have any billnumberversions other than ih
# In the future, we can store these separately in the db and retrieve by billnumber or billnumberversion
@app.get("/bills/{billnumber}", response_model=List[models.BillAndTitle])
def read_bill(billnumber: str, db: Session = Depends(get_db), titlemain: str = None):
    db_bill = crud.get_bill_by_billnumber(db, billnumber=billnumber, titlemain=titlemain)
    print(titlemain)
    if db_bill is None:
        raise HTTPException(status_code=404, detail="Bill {billnumber} not found".format(billnumber=billnumber))
    return db_bill

@app.get("/billid/{bill_id}", response_model=models.Bill)
def read_bill_id(bill_id: int, db: Session = Depends(get_db)):
    db_bill = crud.get_bill(db, bill_id=bill_id)
    if db_bill is None:
        raise HTTPException(status_code=404, detail="Bill not found")
    return db_bill


@app.post("/bills/{bill_id}/titles/", response_model=models.Title)
def create_title_for_bill(
    bill_id: int, title: models.Title, db: Session = Depends(get_db)
):
    return crud.create_bill_title(db=db, title=title)


@app.get("/titles/", response_model=List[models.Title])
def read_titles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    titles = crud.get_titles(db, skip=skip, limit=limit)
    return titles

@app.get("/titles/{title_id}", response_model=models.Title)
def read_title_id(title_id: int, db: Session = Depends(get_db)):
    db_bill = crud.get_title(db, title_id=title_id)
    if db_bill is None:
        raise HTTPException(status_code=404, detail="Title not found")
    return db_bill