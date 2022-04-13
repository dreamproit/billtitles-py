from fastapi import APIRouter

from billtitles.api.api_v1.endpoints import bills, titles

api_router = APIRouter()
api_router.include_router(bills.router, tags=["Bills"])
api_router.include_router(
    titles.router,
    # prefix="/titles",
    tags=["Titles"],
)
