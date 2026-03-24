from fastapi import APIRouter

from app.modules.agent.router import router as agent_router
from app.modules.auth.router import router as auth_router
from app.modules.baby_profile.router import router as baby_profile_router
from app.modules.family.router import router as family_router
from app.modules.growth.router import router as growth_router
from app.modules.media.router import router as media_router
from app.modules.reminder.router import router as reminder_router
from app.modules.vaccine.router import router as vaccine_router

health_router = APIRouter(tags=["health"])
api_router = APIRouter()


# 返回服务健康状态，供本地开发、部署探活和基础监控使用。
@health_router.get("/health")
async def get_health_status() -> dict[str, str]:
    return {"status": "ok"}


api_router.include_router(auth_router)
api_router.include_router(family_router)
api_router.include_router(baby_profile_router)
api_router.include_router(growth_router)
api_router.include_router(vaccine_router)
api_router.include_router(media_router)
api_router.include_router(reminder_router)
api_router.include_router(agent_router)
