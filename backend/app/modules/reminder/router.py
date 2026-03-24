from fastapi import APIRouter

router = APIRouter(prefix="/reminder", tags=["reminder"])


# 返回提醒模块占位信息，用于确认模块路由注册成功。
@router.get("/ping")
async def ping_reminder_module() -> dict[str, str]:
    return {"module": "reminder", "status": "ready"}
