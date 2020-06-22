import aioredis
import pydantic
from fastapi import FastAPI, Depends
from fastapi.logger import logger
from fastapi_plugins import RedisSettings, depends_redis, redis_plugin

app = FastAPI()
KEY = "fastapi_cache_snippet"


class Other(pydantic.BaseSettings):
    pass


class AppSettings(Other, RedisSettings):
    pass


@app.on_event("startup")
async def startup():
    logger.info("server startup")
    config = AppSettings(redis_url="redis://localhost")
    await redis_plugin.init_app(app=app, config=config)
    await redis_plugin.init()


@app.on_event("shutdown")
async def shutdown():
    await redis_plugin.terminate()
    logger.info("server shutdown")


@app.get("/hello/{msg}")
async def hello(msg: str, cache: aioredis.Redis = Depends(depends_redis)):
    c = await cache.get(KEY)
    if c:
        logger.info(f"hit cache: {c}")
    else:
        c = f"Hello {msg}"
        await cache.set(KEY, c)
    return {"msg": c}
