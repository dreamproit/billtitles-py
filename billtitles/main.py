import uvicorn
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from billtitles.config import settings
from billtitles.version import __version__
from billtitles.api.api_v1.api import api_router as api_router_v1


app = FastAPI()


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

app.include_router(api_router_v1, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    uvicorn.run("billtitles.main:app", host="0.0.0.0", port=8000, reload=True)
