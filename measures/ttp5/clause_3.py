from sqlalchemy.orm import Session
from postgres import declarations as tables
from typing import Union
from datetime import datetime, timezone
__description__ = "Импорт товара растёт по состоянию на последнее полугодие или полный календарный год"

def check(session:Session, code:int) -> dict[str,Union[str,float,list]]:
    good = tables.Goods.by_code(session, code)
    if not good: return {"status": "Товар - не найден"}
    now = datetime.now(timezone.utc)
    links = []

    import_history = []
    total_import_value_years, status = good.get_metrics("total_import_value_year")
    if total_import_value_years is None: return {"status": status}
    for total_import_value_year in total_import_value_years[:2]:
        links.append((total_import_value_year.metric.full_name, total_import_value_year.source, (now - total_import_value_year.updated).total_seconds()))
        import_history.append(total_import_value_year.value)

    degree = +1.0 if import_history[0]>import_history[1] else -1.0
    degree = max(min(degree,1.0),-1.0)
    return {
        "status": "OK",
        "degree": degree,
        "links": links
    }
