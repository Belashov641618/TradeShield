from sqlalchemy.orm import Session
from postgres import declarations as tables
from typing import Union
from datetime import datetime, timezone
__description__ = "В отношении товара техническими регламентами ЕАЭС/ПП РФ № 2425 установлено требование о сертификации соответствия"

def check(session:Session, code:int) -> dict[str,Union[str,float,list]]:
    good = tables.Goods.by_code(session, code)
    if not good: return dict(status="Товар - не найден")
    now = datetime.now(timezone.utc)
    links = []

    in_pprf_2425, status = good.get_metric("in_pprf_2425")
    if in_pprf_2425 is None: return {"status": status}
    links.append((in_pprf_2425.metric.full_name, in_pprf_2425.source, (now - in_pprf_2425.updated).total_seconds()))

    degree = +1.0 if in_pprf_2425.value else -1.0
    degree = max(min(degree, 1.0), -1.0)
    return {
        "status": "OK",
        "degree": degree,
        "links": links
    }
