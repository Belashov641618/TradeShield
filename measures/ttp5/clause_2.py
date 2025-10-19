from sqlalchemy.orm import Session
from postgres import declarations as tables
from typing import Union
from datetime import datetime, timezone
__description__ = "Товар отсутствует в Приказе Минпромторга России от 10.09.2024 № 4114"

def check(session:Session, code:int) -> dict[str,Union[str,float,list]]:
    good = tables.Goods.by_code(session, code)
    if not good: return dict(status="Товар - не найден")
    now = datetime.now(timezone.utc)
    links = []

    in_mpt_4114, status = good.get_metric("in_mpt_4114")
    if in_mpt_4114 is None: return {"status": status}
    links.append((in_mpt_4114.metric.full_name, in_mpt_4114.source, (now - in_mpt_4114.updated).total_seconds()))

    degree = +1.0 if in_mpt_4114.value else -1.0
    degree = max(min(degree, 1.0), -1.0)
    return {
        "status": "OK",
        "degree": degree,
        "links": links
    }
