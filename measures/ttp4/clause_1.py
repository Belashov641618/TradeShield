from sqlalchemy.orm import Session
from postgres import declarations as tables
from typing import Union
from datetime import datetime, timezone
__description__ =  "Товар или товары из одной с этим товаром группы ТН ВЭД находится в приложениях к ПП РФ № 1875"

def check(session:Session, code:int) -> dict[str,Union[str,float,list]]:
    good = tables.Goods.by_code(session, code)
    if not good: return dict(status="Товар - не найден")
    now = datetime.now(timezone.utc)
    links = []

    in_pprf_1875, status = good.get_metric("in_pprf_1875")
    if in_pprf_1875 is None: return {"status": status}
    links.append((in_pprf_1875.metric.full_name, in_pprf_1875.source, (now-in_pprf_1875.updated).total_seconds()))

    degree = +1.0 if in_pprf_1875.value else -1.0
    degree = max(min(degree,1.0),-1.0)
    return {
        "status" : "OK",
        "degree" : degree,
        "links" : links
    }
