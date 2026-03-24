from fastapi import APIRouter

router = APIRouter(prefix="/agent", tags=["agent"])


# 返回 Agent 模块占位信息，用于确认模块路由注册成功。
@router.get("/ping")
async def ping_agent_module() -> dict[str, str]:
    return {"module": "agent", "status": "ready"}
