import os
import redis

from fastapi import FastAPI
from celery import Celery
from sqlalchemy import create_engine


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


@celery.task(bind=True)
def data_extractor(self, code:str, name:str, inn:str):
    raise NotImplementedError
