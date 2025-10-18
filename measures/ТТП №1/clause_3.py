from sqlalchemy.orm import Session
from postgres import declarations as tables
from typing import Union
from datetime import datetime, timezone
__description__ = "Производство товара в России удовлетворяет уровень потребления товара в России/ЕАЭС"

def check(session:Session, code:int) -> dict[str,Union[str,float,list]]:
    good = tables.Goods.by_code(session, code)
    if not good: return {"status": "Товар - не найден"}
    now = datetime.now(timezone.utc)

    production, status = good.get_metric("production_russia")
    if production is None: return {"status": status}

    consumption, status = good.get_metric("consumption_russia")
    if consumption is None: return {"status": status}

    degree = +1.0 if production.value >= consumption.value else -1.0
    degree = max(min(degree,1.0),-1.0)

    links = [(metric.metric.full_name, metric.source, (now-metric.updated).total_seconds()) for metric in (production, consumption)]

    return {
        "status": "OK",
        "degree": degree,
        "links": links
    }
