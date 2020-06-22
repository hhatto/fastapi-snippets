from fastapi import FastAPI
from fastapi.logger import logger
from caches import Cache

app = FastAPI()

cache = Cache("redis://localhost", ttl=60)
KEY = "fastapi_cache_snippet"


@app.on_event("startup")
async def startup():
    logger.info("server startup")
    await cache.connect()


@app.on_event("shutdown")
async def shutdown():
    await cache.disconnect()
    logger.info("server shutdown")


@app.get("/hello/{msg}")
async def hello(msg: str):
    c = await cache.get(KEY)
    if c:
        logger.info(f"hit cache: {c}")
    else:
        c = f"Hello {msg}"
        await cache.set(KEY, c)
    return {"msg": c}
