from fastapi import APIRouter

router = APIRouter(prefix="/media", tags=["media"])


# 返回媒体模块占位信息，用于确认模块路由注册成功。
@router.get("/ping")
async def ping_media_module() -> dict[str, str]:
    return {"module": "media", "status": "ready"}
