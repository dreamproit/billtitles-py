from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

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


@app.post("/bills/", response_model=schemas.Bill)
def create_bill(bill: schemas.BillCreate, db: Session = Depends(get_db)):
    db_bill = crud.get_bill_by_billnumber(db, billnumber=bill.billnumber)
    if db_bill:
        raise HTTPException(status_code=400, detail="Billnumber already registered")
    return crud.create_bill(db=db, bill=bill)


@app.get("/bills/", response_model=List[schemas.Bill])
def read_bills(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    bills = crud.get_bills(db, skip=skip, limit=limit)
    return bills


@app.get("/bills/{billnumber}", response_model=schemas.Bill)
def read_bill(billnumber: str, db: Session = Depends(get_db)):
    db_bill = crud.get_bill_by_billnumber(db, billnumber=billnumber)
    if db_bill is None:
        raise HTTPException(status_code=404, detail="Bill not found")
    return db_bill

#@app.get("/bills/{bill_id}", response_model=schemas.Bill)
#def read_bill(bill_id: int, db: Session = Depends(get_db)):
#    db_bill = crud.get_bill(db, bill_id=bill_id)
#    if db_bill is None:
#        raise HTTPException(status_code=404, detail="Bill not found")
#    return db_bill


@app.post("/bills/{bill_id}/titles/", response_model=schemas.Title)
def create_title_for_bill(
    bill_id: int, title: schemas.TitleCreate, db: Session = Depends(get_db)
):
    return crud.create_bill_title(db=db, title=title, bill_id=bill_id)


@app.get("/titles/", response_model=List[schemas.Title])
def read_titles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    titles = crud.get_titles(db, skip=skip, limit=limit)
    return titles