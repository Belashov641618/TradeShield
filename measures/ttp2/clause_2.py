from sqlalchemy.orm import Session
from postgres import declarations as tables
from typing import Union
from datetime import datetime, timezone
__description__ = "Производство товара в России удовлетворяет уровень потребления товара в России"

from measures.ttp1.clause_3 import check as check_
check = check_
