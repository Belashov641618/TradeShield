from sqlalchemy.orm import Session
from postgres import declarations as tables
from typing import Union
from datetime import datetime, timezone
__description__ = "Доля импорта из Китая по состоянию на последний полный календарный год растёт в сравнении с предыдущим трёхлетним периодом"

from measures.ttp2.clause_1 import check as check_
check = check_
