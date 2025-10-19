from sqlalchemy.orm import Session
from postgres import declarations as tables
from typing import Union
from datetime import datetime, timezone
__description__ = "Доля импорта из недружественных стран по перечню распоряжения № 430-р составляет менее 30% по состоянию на последнее полугодие или полный календарный год, доля снижается в сравнении с аналогичным предыдущим периодом"

def check(session:Session, code:int) -> dict[str,Union[str,float,list]]:
    good = tables.Goods.by_code(session, code)
    if not good: return dict(status="Товар - не найден")
    now = datetime.now(timezone.utc)
    links = []

    unfriendly_import_value = 0.
    errors = []
    for country in session.query(tables.Countries).filter_by(unfriendly=True).all():
        import_value, status = good.get_metric("import_value_year", country=country.iso2)
        if import_value is None: errors.append(status)
        unfriendly_import_value += import_value.value
        links.append((import_value.metric.full_name, import_value.source, (now-import_value.updated).total_seconds()))
    if not links: return {"status":errors[0]}

    total_import_value, status = good.get_metric("total_import_value_year")
    if total_import_value is None: return {"status":status}
    links.append((total_import_value.metric.full_name, total_import_value.source, (now-total_import_value.updated).total_seconds()))

    degree = 1.0 if unfriendly_import_value/total_import_value < 0.3 else -1.0
    degree = max(min(degree,1.0),-1.0)

    return {
        "status" : "OK",
        "degree" : degree,
        "links" : links
    }
