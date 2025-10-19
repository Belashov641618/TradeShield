from sqlalchemy.orm import Session
from postgres import declarations as tables
from typing import Union
from datetime import datetime, timezone
__description__ = "Объём производства товара в России сокращается за указанный период (1 год + 3 предыдущих)"

def check(session:Session, code:int) -> dict[str,Union[str,float,list]]:
    good = tables.Goods.by_code(session, code)
    if not good: return dict(status="Товар - не найден")
    now = datetime.now(timezone.utc)
    links = []

    production_history = []
    production_russia_years, status = good.get_metrics("production_russia_year")
    if production_russia_years is None: return {"status": status}
    for production_russia_year in production_russia_years[:4]:
        production_history.append(production_russia_year.value)
        links.append((production_russia_year.metric.full_name, production_russia_year.source, (now-production_russia_year.updated).total_seconds()))

    degree = +1.0 if any([production1 < production0 for production1, production0 in zip(production_history[:-1], production_history[1:])]) else -1.0
    degree = max(min(degree,1.0),-1.0)
    return {
        "status" : "OK",
        "degree" : degree,
        "links" : links
    }
