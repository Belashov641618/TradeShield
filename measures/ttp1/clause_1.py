from sqlalchemy.orm import Session
from postgres import declarations as tables
from typing import Union
from datetime import datetime, timezone
__description__ = "Применяемая ставка таможенного тарифа ЕТТ ЕАЭС меньше предельной ставки в отношении кода, установленной обязательствами России в ВТО"

def check(session:Session, code:int) -> dict[str,Union[str,float,list]]:
    good = tables.Goods.by_code(session, code)
    if not good: return dict(status="Товар - не найден")

    current_duty, status = good.get_metric("current_duty")
    if current_duty is None: return {"status":status}
    vto_duty, status = good.get_metric("vto_duty")
    if vto_duty is None: return {"status": status}

    if vto_duty.value <= current_duty.value:
        degree = -1.0
    else: degree = (vto_duty.value-current_duty.value)/good.vto_duty
    degree = max(min(degree,1.0),-1.0)

    now = datetime.now(timezone.utc)
    return {
        "status" : "OK",
        "degree" : degree,
        "links" : [(metric.metric.ful_name, metric.source, (now-metric.updated).total_seconds()) for metric in (current_duty, vto_duty)]
    }
