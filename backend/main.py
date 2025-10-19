import os
import io
import redis
import redis.asyncio as aioredis
import asyncio

from fastapi import FastAPI, WebSocket
from fastapi.responses import JSONResponse, StreamingResponse
from celery import Celery
from celery.result import AsyncResult
from sqlalchemy import create_engine, cast, String, exists
from sqlalchemy.orm import sessionmaker
from typing import Optional, Union

from workers import data_extractor
from workers.report_creator import report_creator
from postgres.declarations import Base, tables

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


@app.get("/api/autocomplete")
def autocomplete(code:str="", name:str=""):
    if name != "":      goods = session.query(tables.Goods).filter(cast(tables.Goods.code,String).startswith(name)).all()
    elif code != "":    goods = session.query(tables.Goods).filter(cast(tables.Goods.code,String).startswith(code)).all()
    else:               goods = session.query(tables.Goods).all()
    print(f"[DEBUG] code='{code}', name='{name}', goods found: {len(goods)}")
    for g in goods:
        print(f"[DEBUG] Goods: code={g.code}, name={g.name}")
    code_ = f""
    name_ = f""
    exists_ = session.query(exists().where(tables.Goods.code==int(code))).scalar() if code != "" else False
    if goods is not None and goods:
        best_rarity, best_good = None, goods[0]
        for good in goods:
            rarity = tables.Rarities.rarity(session, good, trigger=False)
            if best_rarity is None or rarity > best_rarity:
                best_rarity = rarity
                best_good = good
        code_ = best_good.code
        name_ = best_good.name
        print(f"[DEBUG] best_good: code={code_}, name={name_}, rarity={best_rarity}")
    return JSONResponse(dict(code=code_,name=name_,exists=exists_))


@app.post("/api/analyze")
def analyze(code:str, name:str, inn:str):
    task = data_extractor.delay(code, name, inn)
    return JSONResponse(dict(job=task.id))
@app.get("/api/result/{job}")
def result(job:str):
    task = AsyncResult(job, app=celery)
    if task.ready():
        return JSONResponse(task.result)
    return JSONResponse(dict(status=task.status))


@app.post("/api/report")
def report(actions:dict[str,dict[str,Union[str,dict[str,Union[str,float]],bool,list[tuple[str,str,float]]]]]):
    task = report_creator.delay(actions)
    return JSONResponse(dict(job=task.id))
@app.get("/api/report/{job}")
def download(job:str):
    task = AsyncResult(job, app=celery)
    if task.ready():
        return StreamingResponse(io.BytesIO(task.result), media_type="application/pdf", headers={"Content-Disposition":"attachment;filename=report.pdf"})
    return JSONResponse(dict(status=task.status))


@app.websocket("/ws/{task_id}")
async def websocket_status(ws:WebSocket, task_id:str):
    await ws.accept()
    channel = f"task_{task_id}"
    redis_url = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
    aioredis_client = await aioredis.from_url(redis_url, decode_responses=True)
    pubsub = aioredis_client.pubsub()
    await pubsub.subscribe(channel)
    try:
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message:
                try: await ws.send_text(message["data"])
                except Exception: continue
            await asyncio.sleep(0.1)
    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"WebSocket error for task {task_id}: {e}")
    finally:
        try:
            await pubsub.unsubscribe(channel)
            await pubsub.close()
        except Exception: pass
        await aioredis_client.close()
        await ws.close()
