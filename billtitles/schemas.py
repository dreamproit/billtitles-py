from pydantic import create_model
from . import models

# For display

BillTitlePlus = create_model(
    'BillTitlePlus',
    titles=str,
    __base__=models.BillTitle,
)

BillToBillPlus = create_model(
    'BillToBillPlus',
    titles=list[str],
    titles_whole_bill=list[str],
    __base__=models.BillToBill,
)