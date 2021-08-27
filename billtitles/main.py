from typing import List, Dict

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

@app.get("/bills/{billnumber}" )
def read_bills(db: Session = Depends(get_db), billnumber: str = None):
    db_bill = crud.get_bill_by_billnumber(db, billnumber=billnumber)
    if db_bill is None:
        raise HTTPException(status_code=404, detail="Bill {billnumber} not found".format(billnumber=billnumber))
    return db_bill

@app.get("/bills/" )
def read_bills_param(db: Session = Depends(get_db), billnumber: str = None, skip: int = 0, limit: int = 100):
    if not billnumber:
        db_bill = crud.get_bills(db, skip=skip, limit=limit)
    else:
        db_bill = crud.get_bill_by_billnumber(db, billnumber=billnumber)
    if db_bill is None:
        raise HTTPException(status_code=404, detail="Bill {billnumber} not found".format(billnumber=billnumber))
    return db_bill

@app.get("/titles/{title_id}" )
def read_title(title_id: int, db: Session = Depends(get_db) ):
    db_bill = crud.get_title(db, title_id=title_id)
    if db_bill is None:
        raise HTTPException(status_code=404, detail="Title with id {title_id} not found".format(title_id=title_id))
    return db_bill

@app.get("/titles/" )
def read_titles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), title_id: int = None, title: str = None):
    if not title_id and not title:
        return crud.get_titles(db, skip=skip, limit=limit)
    db_bill = crud.get_title(db, title_id=title_id, title=title)
    if db_bill is None:
        raise HTTPException(status_code=404, detail="Title not found")
    return db_bill