from sqlalchemy.orm import Session
from postgres import declarations as tables
from typing import Union
from datetime import datetime, timezone
__description__ = "Не выполняются иные критерии для ответов на запрос 1-5, не связанные с критерием «объём импорта»"

from measures.ttp1.clause_2 import check as check_1_2
from measures.ttp2.clause_1 import check as check_2_1
from measures.ttp3.clause_1 import check as check_3_1
from measures.ttp5.clause_3 import check as check_5_3
checks = [check_1_2, check_2_1, check_3_1, check_5_3]

def check(session:Session, code:int) -> dict[str,Union[str,float,list]]:
    triggers = []
    links = []
    for check_ in checks:
        result = check_(session, code)
        if "degree" not in result.keys(): return result
        triggers = result["degree"] < 0.
        links = links + result["links"]
    degree = +1.0 if not all(triggers) else -1.0
    degree = max(min(degree, 1.0), -1.0)
    return {
        "status": "OK",
        "degree": degree,
        "links": links
    }