from sqlalchemy.orm import Session
from postgres import declarations as tables
from typing import Union
from datetime import datetime, timezone
__description__ = "Производство товара в России растёт"

def check(session:Session, code:int) -> dict[str,Union[str,float,list]]:
    good = tables.Goods.by_code(session, code)
    if not good: return {"status": "Товар - не найден"}
    now = datetime.now(timezone.utc)
    links = []

    production_history = []
    production_russia_years, status = good.get_metrics("production_russia_year")
    if production_russia_years is None: return {"status": status}
    for production_russia_year in production_russia_years[:2]:
        links.append((production_russia_year.metric.full_name, production_russia_year.source, (now - production_russia_year.updated).total_seconds()))
        production_history.append(production_russia_year.value)

    degree = +1.0 if production_history[0]>production_history[1] else -1.0
    degree = max(min(degree,1.0),-1.0)
    return {
        "status": "OK",
        "degree": degree,
        "links": links
    }
