from fastapi import APIRouter

router = APIRouter(prefix="/vaccine", tags=["vaccine"])


# 返回疫苗模块占位信息，用于确认模块路由注册成功。
@router.get("/ping")
async def ping_vaccine_module() -> dict[str, str]:
    return {"module": "vaccine", "status": "ready"}
