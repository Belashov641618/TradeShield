from sqlalchemy.orm import Session
from postgres import declarations as tables
from typing import Union
from datetime import datetime, timezone
__description__ = "Объём импорта товара из всех стран превышает объём производства товара в России"

def check(session:Session, code:int) -> dict[str,Union[str,float,list]]:
    good = tables.Goods.by_code(session, code)
    if not good: return dict(status="Товар - не найден")
    now = datetime.now(timezone.utc)
    links = []

    total_import_value_year, status = good.get_metric("total_import_value_year")
    if total_import_value_year is None: return {"status": status}
    links.append((total_import_value_year.metric.full_name, total_import_value_year.source, (now - total_import_value_year.updated).total_seconds()))

    production_russia_year, status = good.get_metric("production_russia_year")
    if production_russia_year is None: return {"status": status}
    links.append((production_russia_year.metric.full_name, production_russia_year.source, (now - production_russia_year.updated).total_seconds()))

    degree = +1.0 if total_import_value_year > production_russia_year else -1.0
    degree = max(min(degree, 1.0), -1.0)
    return {
        "status": "OK",
        "degree": degree,
        "links": links
    }
