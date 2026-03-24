from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router, health_router
from app.core.config import settings
from app.core.lifespan import app_lifespan


# 创建并返回 FastAPI 应用实例，同时挂载全局配置、生命周期和文档信息。
def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=app_lifespan,
    )
    register_middlewares(app)
    register_routers(app)
    return app


# 注册全局中间件，当前先提供基础跨域能力，便于前后端分离调试。
def register_middlewares(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# 注册健康检查路由和所有业务模块路由，保持入口文件只负责装配。
def register_routers(app: FastAPI) -> None:
    app.include_router(health_router)
    app.include_router(api_router, prefix=settings.api_v1_prefix)


app = create_application()
