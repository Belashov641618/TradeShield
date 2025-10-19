import os
import redis

from json import dumps
from fastapi import FastAPI
from celery import Celery
from sqlalchemy import create_engine
from typing import Union


REDIS_HOST          = str(os.getenv("REDIS_HOST",           "localhost"))
REDIS_PORT          = int(os.getenv("REDIS_PORT",           6379))
POSTGRES_HOST       = str(os.getenv("POSTGRES_HOST",        "localhost"))
POSTGRES_PORT       = int(os.getenv("POSTGRES_PORT",        6379))
POSTGRES_DATABASE   = str(os.getenv("POSTGRES_DATABASE",    "default"))
POSTGRES_USER       = str(os.getenv("POSTGRES_USER",        "root"))
POSTGRES_PASSWORD   = str(os.getenv("POSTGRES_PASSWORD",    "password"))


app = FastAPI(title="TradeShield")
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
celery = Celery("tasks", broker=f"redis://{REDIS_HOST}:{REDIS_PORT}/0", backend=f"redis://{REDIS_HOST}:{REDIS_PORT}/1")
engine = create_engine(f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}")

@celery.task(bind=True)
def report_creator(self, actions:dict[str,dict[str,Union[str,dict[str,Union[str,float]],bool,list[tuple[str,str,float]]]]]):
    from time import sleep
    for i in range(100):
        prog = dict(prog=float(i+1), eta=None, step="Процесс генерации")
        redis_client.publish(f"task_{self.request.id}", dumps(prog))
        self.update_state(state="PROGRESS", meta=prog)
        sleep(0.25)
    with open("default.pdf", "rb") as file:
        data = file.read()
    return data
