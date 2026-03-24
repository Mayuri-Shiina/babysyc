from fastapi import APIRouter

router = APIRouter(prefix="/growth", tags=["growth"])


# 返回成长记录模块占位信息，用于确认模块路由注册成功。
@router.get("/ping")
async def ping_growth_module() -> dict[str, str]:
    return {"module": "growth", "status": "ready"}
