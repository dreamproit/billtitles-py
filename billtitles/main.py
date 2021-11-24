from typing import List, Dict

from fastapi import Depends, FastAPI, HTTPException
from fastapi.openapi.utils import get_openapi
from sqlalchemy.orm import Session
from sqlmodel import SQLModel

from . import crud, models, schemas
from .database import SessionLocal, engine
from .version import __version__

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

#@app.get("/bills/related/{billnumber}", response_model=List[schemas.BillToBillPlus])
@app.get("/bills/related/{billnumber}")
def related_bills(db: Session = Depends(get_db), billnumber: str = None) -> List[schemas.BillToBillPlus]:
    db_bills = crud.get_related_bills_w_titles(db, billnumber=billnumber)
    if db_bills is None:
        raise HTTPException(status_code=404, detail="Bills related to {billnumber} not found".format(billnumber=billnumber))
    return db_bills

@app.get("/bills/titles/{billnumber}", response_model=models.BillTitleResponse)
def read_bills(db: Session = Depends(get_db), billnumber: str = None) -> models.BillTitleResponse:
    db_bill = crud.get_bill_titles_by_billnumber(db, billnumber=billnumber)
    if db_bill is None:
        raise HTTPException(status_code=404, detail="Bill {billnumber} not found".format(billnumber=billnumber))
    return db_bill

#@app.get("/bills/" )
#def read_bills_param(db: Session = Depends(get_db), billnumber: str = None, skip: int = 0, limit: int = 100):
#    if not billnumber:
#        db_bill = crud.get_bills(db, skip=skip, limit=limit)
#    else:
#        db_bill = crud.get_bill_by_billnumber(db, billnumber=billnumber)
#    if db_bill is None:
#        raise HTTPException(status_code=404, detail="Bill {billnumber} not found".format(billnumber=billnumber))
#    return db_bill

@app.post("/related/" )
def create_related(db: Session = Depends(get_db)):
    # TODO: Use POST data to create a new related bill
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

@app.post("/titles/" )
def add_title_to_db(title: str, billnumbers: List[str], db: Session = Depends(get_db), is_for_whole_bill: bool = False):
    return crud.add_title(db, title=title, billnumber=billnumbers, is_for_whole_bill=is_for_whole_bill)

@app.delete("/titles/" )
def remove_title_from_db(title: str, db: Session = Depends(get_db)):
    return crud.remove_title(db, title=title)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="BillTitles API",
        version=__version__,
        description="API for related bills",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi