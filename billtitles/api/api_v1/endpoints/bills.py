from typing import List, Optional

import structlog
from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session

import billtitles.schemas
from billtitles import crud
from billtitles.api.deps import get_db

BILL_VERSION_DEFAULT = "--"

router = APIRouter()
logger = structlog.getLogger()
logger.info("api.bills")


# SQLModel.metadata.create_all(engine)

# Run in uvicorn with:
# uvicorn billtitles.main:app --reload


# @router.get(
#     "/bills/related",
#     response_model=List[Union[models.BillToBillModel, models.BillToBillModelDeep]]
# )
# @router.get(
#     "/bills/related/{billnumber}",
#     response_model=List[Union[models.BillToBillModel, models.BillToBillModelDeep]]
# )
# @router.get(
#     "/bills/related/{billnumber}/{version}",
#     response_model=List[Union[models.BillToBillModel, models.BillToBillModelDeep]]
# )


@router.get("/bills/related")
@router.get("/bills/related/{billnumber}")
@router.get("/bills/related/{billnumber}/{version}")
def related_bills(
    billnumber: str,
    version: Optional[str] = BILL_VERSION_DEFAULT,
    flat: Optional[bool] = True,
    billsonly: Optional[bool] = False,
    db: Session = Depends(get_db),
):
    # if version is None:
    #     version = BILL_VERSION_DEFAULT
    # TODO: get the latest version of the bill and get results from that
    db_bills = crud.get_related_bills(
        db,
        billnumber=billnumber,
        version=version,
        flat=flat,
        billsonly=billsonly,
    )
    if db_bills is None:
        raise HTTPException(
            status_code=404,
            detail="Bills related to {billnumber} ({version}) not found".format(
                billnumber=billnumber, version=version
            ),
        )
    return db_bills


@router.get(
    "/bills/titles/{billnumber}", response_model=billtitles.schemas.BillTitleResponse
)
def read_bills(
    billnumber: str, db: Session = Depends(get_db)
) -> billtitles.schemas.BillTitleResponse:
    db_bill = crud.get_bill_titles_by_billnumber(db, billnumber=billnumber)
    if db_bill is None:
        raise HTTPException(
            status_code=404,
            detail="Bill {billnumber} not found".format(billnumber=billnumber),
        )
    return db_bill


@router.post("/related/")
def create_related(db: Session = Depends(get_db)):
    # TODO: Use POST data to create a new related bill
    if db is None:
        raise HTTPException(
            status_code=404,
            detail="Bill {billnumber} not found".format(billnumber=billnumber),
        )
    return db
