from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI


# 管理应用启动和关闭生命周期，后续用于接入数据库、缓存和任务队列初始化。
@asynccontextmanager
async def app_lifespan(_: FastAPI) -> AsyncIterator[None]:
    yield
