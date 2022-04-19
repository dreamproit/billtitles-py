from typing import List
from typing import Optional

from sqlalchemy.orm import Session

from billtitles.api import deps

from billtitles import models  # BillBasic, BillStageTitle

from billtitles import utils
from billtitles.api.deps import get_db
from billtitles.database import SessionLocal
from billtitles.documents import BillStageTitleDocument
from billtitles.schemas import BillMatchingTitlesResponse
from billtitles.schemas import BillsTitlesResponse
from billtitles.schemas import BillTitlesResponse
from billtitles.schemas import ErrorResponse
from elasticsearch_dsl import Q
from fastapi import APIRouter
from fastapi import Depends
from starlette.responses import JSONResponse

# from billtitles.celery import app as celery_app

router = APIRouter()


def get_bill_titles_by_billnumber(billnumber: str, db: SessionLocal = Depends(get_db)):
    """Get bill titles and titlesNoYear by billnumber

    Returns:
        tuple
    """
    bill = db.query(models.BillBasic).filter(models.BillBasic.bill_number == billnumber)

    df = BillStageTitleDocument.search().filter(
        Q("match", **{"bill_basic.bill_number": billnumber})
    )
    dfr = df.execute()
    hits_total = dfr.hits.total.value
    bst_data = df[:hits_total].to_queryset().distinct()
    titles = {}
    titlesNoYear = {}
    for bst in bst_data:
        tf = BillStageTitleDocument.search().filter(Q("match_phrase", title=bst.title))
        tfr = tf.execute()
        tf_hits = tfr.hits.total.value
        tf_data = tf[:tf_hits].to_queryset().distinct()
        bills_containing_title = [title.bill_basic.bill_number for title in tf_data]

        tnyf = BillStageTitleDocument.search().filter(
            Q("match_phrase", titleNoYear=bst.titleNoYear)
        )
        tnyfr = tnyf.execute()
        tnyf_hits = tnyfr.hits.total.value
        tnyf_data = tnyf[:tnyf_hits].to_queryset().distinct()
        bills_containing_titleNoYear = [
            titleNoYear.bill_basic.bill_number for titleNoYear in tnyf_data
        ]

        titles[bst.title] = bills_containing_title
        titlesNoYear[bst.titleNoYear] = bills_containing_titleNoYear
    return titles, titlesNoYear


def get_bill_stage_titles_by_billnumber(billnumber: str):
    """Get bill stage titles by bill number

    Returns:
        tuple
    """
    df = BillStageTitleDocument.search().filter(
        Q("match", **{"bill_basic.bill_number": billnumber})
    )
    dfr = df.execute()
    hits_total = dfr.hits.total.value
    bst_data = df[:hits_total].to_queryset().distinct()
    titles = [bst.title for bst in bst_data]
    titlesNoYear = [bst.titleNoYear for bst in bst_data]
    return titles, titlesNoYear


@router.get(
    "/bills/titles/{billnumber}",
    summary="Retrieve titles and titlesNoYear information for a specific bill.",
    tags=["bill-titles-by-bill"],
    response_model=BillTitlesResponse,
)
def get_bill_titles_by_bill(
    bill_titles_by_billnumber=Depends(get_bill_titles_by_billnumber),
):
    """Get bill titles by bill number

    Args:
        billnumber (str): bill number

    Returns:
        BillTitlesResponse
    """
    (
        titles,
        titlesNoYear,
    ) = bill_titles_by_billnumber  # get_bill_titles_by_billnumber(billnumber)
    return BillTitlesResponse(titles=titles, titlesNoYear=titlesNoYear)


@router.get(
    "/bills/titles",
    summary="Retrieve titles and titlesNoYear information for the dedicated bills.",
    tags=["bill-titles-by-bills"],
    name="get-bill-titles-by-bills",
    response_model=BillsTitlesResponse,
)
def get_bill_titles_by_bills(bills: List[str] = Depends(deps.parse_list)):
    """Get bill titles by billnumber list

    Args:
        bills (List[str], optional): billnumbers list. Defaults to Depends(parse_list).

    Returns:
        BillsTitlesResponse or JSONResponse
    """
    bill_titles = {}
    if bills:
        for bill in bills:
            titles, titlesNoYear = get_bill_titles_by_billnumber(bill)
            bill_titles[bill] = dict(titles=titles, titlesNoYear=titlesNoYear)
        return bill_titles
    else:
        return JSONResponse(
            {"Warn": "Bill numbers list not provided."}, status_code=400
        )


@router.get(
    "/titles/{title}",
    summary=(
        "Retrieve titles and titlesNoYear "
        "information that matches to a specific title."
    ),
    tags=["get-matching-titles"],
    name="get-matching-titles",
    response_model=BillMatchingTitlesResponse,
)
def get_matching_titles(
    title: str,
    fuzzy: Optional[bool] = False,
    limit: int = 10,
    offset: int = 0,
    from_db: bool = True,
    db: Session = Depends(get_db),
):
    """Get matching titles

    Args:
        title (str): title that you want to match
        fuzzy (Optional[bool], optional): fuzzy param. Defaults to True.
        limit (int, optional): limit param. Defaults to 10.
        offset (int, optional): offset param. Defaults to 0.
        db (Session): db connection session.
    Returns:
        BillMatchingTitlesResponse or JSONResponse
    """
    if from_db:
        titles = db.query(Tit)

    slop = len(title.split()) - 1

    def build_match_q(field):
        return Q(
            "match",
            **{
                field: dict(
                    query=title,
                    fuzziness=4,
                    boost=1,
                )
            },
        )

    def build_match_phrase_q(field):
        return Q(
            "match_phrase",
            **{
                field: dict(
                    query=title,
                    slop=slop,
                    boost=20,
                )
            },
        )

    if fuzzy:
        query = (build_match_q("title") | build_match_phrase_q("title")) | (
            build_match_q("titleNoYear") | build_match_phrase_q("titleNoYear")
        )
        df = BillStageTitleDocument.search().query(query)
    else:
        df = BillStageTitleDocument.search().filter(
            Q("match_phrase", title=title) | Q("match_phrase", titleNoYear=title)
        )
    df = df.sort({"_score": "desc"})
    dfr = df.execute()

    hits_total = dfr.hits.total.value
    bst_data = df[:limit].to_queryset().distinct()
    titles = []
    titlesNoYear = []
    for bst in bst_data:
        titles.append(bst.title)
        titlesNoYear.append(bst.titleNoYear)
    return BillMatchingTitlesResponse(
        titles=titles,
        titlesNoYear=titlesNoYear,
        hitsTotal=hits_total,
    )


@router.post(
    "/bills/titles/{billnumber}",
    summary="Add new title to a specific bill data.",
    tags=["add-new-title-to-bill"],
    response_model=BillMatchingTitlesResponse,
    responses={
        200: {
            "model": BillMatchingTitlesResponse,
            "description": "Item created",
        },
        404: {
            "model": ErrorResponse,
            "description": "Item was not found",
        },
    },
    name="add-new-title-to-bill",
)
def add_new_title_to_bill(billnumber: str, title: str):
    """Add new title to a specific bill dataset

    Args:
        billnumber (str): bill number
        title (str): title that you want to add

    Returns:
        BillMatchingTitlesResponse or JSONResponse
    """
    bill_basic = models.BillBasic.objects.filter(bill_number=billnumber).first()
    if bill_basic:
        models.BillStageTitle.objects.get_or_create(
            bill_basic=bill_basic,
            title=title,
            titleNoYear=utils.get_titleNoYear(title),
        )
        titles, titlesNoYear = get_bill_stage_titles_by_billnumber(
            bill_basic.bill_number
        )
        return BillMatchingTitlesResponse(titles=titles, titlesNoYear=titlesNoYear)
    else:
        return ErrorResponse(
            **{"error": f"Can not find bill depending on this {billnumber}"},
        )


@router.get("/scrape/", tags=["utils"], status_code=200)
def run_celery_scrape():
    """Run scrape process in background, using celery worker."""
    # celery_app.send_task("btiapp.tasks.scrape_bills")
    return {"result": "running task scrape_bills"}


@router.get("/pipeline/", tags=["utils"], status_code=200)
def run_celery_pipeline():
    """Run pipeline process in background, using celery worker."""
    # celery_app.send_task("btiapp.tasks.run_pipeline")
    return {"result": "running task run_pipeline"}
