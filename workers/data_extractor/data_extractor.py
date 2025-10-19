import math
import os
import redis
import json

from typing import Union
from json import dumps
from fastapi import FastAPI
from celery import Celery
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone

from postgres.declarations import Base
from utilities import gitpull, load_clauses

from postgres.declarations import tables

REDIS_HOST          = str(os.getenv("REDIS_HOST",           "localhost"))
REDIS_PORT          = int(os.getenv("REDIS_PORT",           6379))
POSTGRES_HOST       = str(os.getenv("POSTGRES_HOST",        "localhost"))
POSTGRES_PORT       = int(os.getenv("POSTGRES_PORT",        5432))
POSTGRES_DATABASE   = str(os.getenv("POSTGRES_DATABASE",    "default"))
POSTGRES_USER       = str(os.getenv("POSTGRES_USER",        "root"))
POSTGRES_PASSWORD   = str(os.getenv("POSTGRES_PASSWORD",    "password"))


app = FastAPI(title="TradeShield")
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
celery = Celery("tasks", broker=f"redis://{REDIS_HOST}:{REDIS_PORT}/0", backend=f"redis://{REDIS_HOST}:{REDIS_PORT}/1")

engine = create_engine(f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


@celery.task(bind=True)
def data_extractor(self, code:str, name:str, inn:str) -> dict[str,dict[str,Union[str,dict[str,Union[str,float]],bool,list[tuple[str,str,float]]]]]:
    """
    measure_name:
        description: str <Описание меры>
        recommend: bool <Выполнены ли все условия меры>
        links: [(str <полное имя метрики>, str <источник данных>, float <данные получены секунд назад>),...]
        clauses:
            status: str <"OK" либо причина почему не удалось получить данные>
            degree(OPTIONAL): float <число от -1 до +1 -> условие не выполнено или условие выполнено>
            state(OPTIONAL): bool <выполнено ли условие>
    """
    good = tables.Goods.by_code(int(code))
    session.add(tables.Requests(
        good=good,
        inn=inn,
        source="frontend",
        timestamp=datetime.now(timezone.utc)
    ))
    session.commit()
    tables.Rarities.rarity(good, trigger=True)

    prog = dict(prog=0.0,eta=None,step="Загрузка мер")
    redis_client.publish(f"task_{self.request.id}", dumps(prog))
    self.update_state(state="PROGRESS", meta=prog)

    gitpull(__file__)

    prog = dict(prog=0.0, eta=None, step="Обработка мер")
    redis_client.publish(f"task_{self.request.id}", dumps(prog))
    self.update_state(state="PROGRESS", meta=prog)

    data:dict = {}
    measures = os.path.abspath(os.path.join(os.path.dirname(__file__),"../measures"))
    directories = os.listdir(measures)

    for i, directory in enumerate(directories):
        if os.path.isdir(directory):
            clauses = load_clauses(os.path.join(measures, directory))
            with open(os.path.join(measures,"description.json"), "r") as file:
                description = json.load(file)
            name, description = description["name"], description["description"]

            prog = dict(prog=100*i/len(directories), eta=None, step=f"{name}")
            redis_client.publish(f"task_{self.request.id}", dumps(prog))
            self.update_state(state="PROGRESS", meta=prog)

            data[name] = {"description":description, "clauses":[], "recommend":False, "links":[]}
            links = []
            triggers = []
            for desc, check in clauses:
                clause_result = check(session, int(code))
                links_ = []
                if "links" in clause_result:
                    links_ = clause_result.pop("links")
                if "degree" in clause_result:
                    links = links + links_
                    clause_result["state"] = clause_result["degree"]>0
                    triggers.append(clause_result["state"])
                data[name]["clauses"].append(clause_result)
            data[name]["links"] = list(set(links))
            if triggers: data[name]["recommend"] = all(triggers)

    prog = dict(prog=100, eta=None, step=f"Отправка результата")
    redis_client.publish(f"task_{self.request.id}", dumps(prog))
    self.update_state(state="PROGRESS", meta=prog)

    return data






