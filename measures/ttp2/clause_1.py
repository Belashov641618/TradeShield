from sqlalchemy.orm import Session
from postgres import declarations as tables
from typing import Union
from datetime import datetime, timezone
__description__ = "Доля импорта из Китая по состоянию на последний полный календарный год растёт в сравнении с предыдущим трёхлетним периодом"

def check(session:Session, code:int) -> dict[str,Union[str,float,list]]:
    good = tables.Goods.by_code(session, code)
    if not good: return dict(status="Товар - не найден")
    now = datetime.now(timezone.utc)
    links = []

    china_import_current, status = good.get_metric("import_value_year", country="CN")
    if china_import_current is None: return {"status": status}
    links.append((china_import_current.metric.full_name, china_import_current.source, (now-china_import_current.updated).total_seconds()))

    total_import_current, status = good.get_metric("total_import_value_year")
    if total_import_current is None: return {"status": status}
    links.append((total_import_current.metric.full_name, total_import_current.source, (now-total_import_current.updated).total_seconds()))

    chine_import_3years = 0.
    china_import_years, status = good.get_metrics("import_value_year", country="CN")
    if china_import_years is None: return {"status": status}
    for china_import_year in china_import_years[1:4]:
        chine_import_3years += china_import_year.value
        links.append((china_import_year.metric.full_name, china_import_year.source, (now-china_import_year.updated).total_seconds()))

    total_import_3years = 0.
    total_import_years, status = good.get_metrics("total_import_value_year")
    if total_import_years is None: return {"status": status}
    for total_import_year in total_import_years[1:4]:
        total_import_3years += total_import_year.value
        links.append((total_import_year.metric.full_name, total_import_year.source, (now-total_import_year.updated).total_seconds()))

    ratio_current = china_import_current/total_import_current
    ratio_3years = chine_import_3years/china_import_current
    degree = +1.0 if ratio_current > ratio_3years else -1.0
    degree = max(min(degree,1.0),-1.0)
    return {
        "status" : "OK",
        "degree" : degree,
        "links" : links
    }
