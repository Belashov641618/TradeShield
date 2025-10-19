from sqlalchemy.orm import Session
from postgres import declarations as tables
from typing import Union
from datetime import datetime, timezone
__description__ = "Расчётная средняя контрактная цена товаров из Китая ниже СКЦ импортируемых из прочих стран товаров"

def check(session:Session, code:int) -> dict[str,Union[str,float,list]]:
    good = tables.Goods.by_code(session, code)
    if not good: return dict(status="Товар - не найден")
    now = datetime.now(timezone.utc)
    links = []

    avg_prices = []
    errors = []
    for country in session.query(tables.Countries).filter(tables.Countries.name!="CN").all():
        avg_price, status = good.get_metric("avg_price", country=country.iso2)
        if avg_price is None: errors.append(status)
        avg_prices.append(avg_price.value)
        links.append((avg_price.metric.full_name, avg_price.source, (now - avg_price.updated).total_seconds()))
    if not links: return {"status": errors[0]}
    avg_prices = sum(avg_prices)/len(avg_prices)

    china_avg_price, status = good.get_metric("avg_price", country="CN")
    if china_avg_price is None: return {"status": status}
    links.append((china_avg_price.metric.full_name, china_avg_price.source, (now-china_avg_price.updated).total_seconds()))

    degree = +1.0 if china_avg_price < avg_prices else -1.0
    degree = max(min(degree,1.0),-1.0)
    return {
        "status" : "OK",
        "degree" : degree,
        "links" : links
    }
