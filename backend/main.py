import os
import io
import redis
import psycopg2

from fastapi import FastAPI
from fastapi.responses import JSONResponse, StreamingResponse
from celery import Celery
from celery.result import AsyncResult
from psycopg2.extras import RealDictCursor
from typing import Optional


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
connection = psycopg2.connect(host=POSTGRES_HOST, port=POSTGRES_PORT, dbname=POSTGRES_DATABASE, user=POSTGRES_USER, password=POSTGRES_PASSWORD)
cursor = connection.cursor(cursor_factory=RealDictCursor)


@app.get("/api/autocomplete")
def autocomplete(code:str="", name:str=""):
    # TODO Работа с базой данных Postgres через cursor
    code_ = f"{code}60065"
    name_ = f"{name}ый скот"
    exist = len(code) > 6
    return JSONResponse(dict(code=code_,name=name_,exist=exist))

@app.post("/api/analyze")
def analyze(code:str, name:str, inn:str):
    # TODO Импортировать celery_analyze
    task = celery_analyze.delay(code, name, inn)
    return JSONResponse(dict(job=task.id))

@app.get("/api/result/{job}")
def result(job:str):
    task = AsyncResult(job, app=celery)
    if task.ready():
        return JSONResponse(task.result)
    return JSONResponse(dict(status=task.status))

@app.post("/api/report")
def report(actions:Optional[dict[str,dict[str,str]]]=None):
    # TODO Импортировать celery_report
    task = celery_report.delay(actions)
    return JSONResponse(dict(job=task.id))

@app.get("/api/report/{job}")
def download(job:str):
    task = AsyncResult(job, app=celery)
    if task.ready():
        return StreamingResponse(io.BytesIO(task.result), media_type="application/pdf", headers={"Content-Disposition":"attachment;filename=report.pdf"})
    return JSONResponse(dict(status=task.status))
