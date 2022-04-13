import pprint as pp

from billtitles.api.deps import get_db
from billtitles.models import *


if __name__ == "__main__":
    db = next(get_db())
    q = (
        db.query(Bill, BillBasic, BillStageTitle, BillTitles)
        .filter(
            BillBasic.bill_number == Bill.billnumber,
            BillStageTitle.bill_basic_id == BillBasic.id,
            BillTitles.bill_basic_id == BillBasic.id,
        )
        .limit(10)
        .all()
    )
    pp.pprint(q)
    pp.pp(1)
