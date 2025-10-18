from sqlalchemy.orm import Session
from postgres import declarations as tables
from typing import Union
from datetime import datetime, timezone
__description__ = "Применяемая ставка таможенного тарифа ЕТТ ЕАЭС меньше предельной ставки в отношении кода, установленной обязательствами России в ВТО."

def check(session:Session, code:int) -> dict[str,Union[str,float,list]]:
    good = session.query(tables.Goods).filter_by(code=code).first()
    if not good:                    return dict(status="Товар - не найден")
    if good.current_duty is None:   return dict(status="Применяемая ставка таможенного тарифа ЕТТ ЕАЭС - не найден")
    if good.vto_duty is None:       return dict(status="Ставка ВТО - не найден")

    updated_delta = datetime.now(timezone.utc) - good.updated_at
    degree = max(min((good.vto_duty-good.current_duty)/good.vto_duty,1.0),-1.0)

