from datetime import datetime, timezone
from uuid import uuid4

import httpx
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.models.agent import AgentMessage, AgentSession
from app.models.baby import Baby
from app.models.family import Family
from app.models.user import User
from app.schemas.agent import (
    AgentMessageData,
    AgentMessageListResponse,
    AgentSessionData,
    AgentSessionListResponse,
    AgentSessionResponse,
    CreateAgentMessageRequest,
    CreateAgentMessageResponse,
    CreateAgentSessionRequest,
)
from app.schemas.common import ActorMeta, BabyContextMeta, ResponseMeta
from app.services.agent_service import generate_agent_reply

router = APIRouter(prefix="/agent", tags=["agent"])


# 构建 Agent 模块统一响应元信息，附带当前操作者和宝宝上下文。
def build_agent_meta(user: User, baby: Baby, permissions: list[str]) -> ResponseMeta:
    age_days = max((datetime.now().date() - baby.birth_date).days, 0)
    return ResponseMeta(
        actor=ActorMeta(user_id=user.id, display_name=user.display_name, role="SuperOwner"),
        baby_context=BabyContextMeta(
            baby_id=baby.id,
            baby_name=baby.nickname,
            age_days=age_days,
            age_months=age_days // 30,
        ),
        timestamp=datetime.now(timezone.utc).isoformat(),
        permissions=permissions,
    )


# 将会话模型转换为统一响应结构。
def build_agent_session_data(session: AgentSession) -> AgentSessionData:
    return AgentSessionData(
        session_id=session.id,
        family_id=session.family_id,
        baby_id=session.baby_id,
        created_by_user_id=session.created_by_user_id,
        title=session.title,
        status=session.status,
        last_message_at=session.last_message_at.isoformat() if session.last_message_at else None,
    )


# 将消息模型转换为统一响应结构。
def build_agent_message_data(message: AgentMessage) -> AgentMessageData:
    return AgentMessageData(
        message_id=message.id,
        session_id=message.session_id,
        family_id=message.family_id,
        baby_id=message.baby_id,
        role=message.role,
        input_type=message.input_type,
        content=message.content,
        risk_level=message.risk_level,
        created_at=message.created_at.isoformat(),
    )


# 获取 Agent 接口所需的宝宝、家庭和操作者上下文。
def resolve_agent_context(db: Session, family_id: str, baby_id: str) -> tuple[Baby, Family, User]:
    baby = db.get(Baby, baby_id)
    if baby is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Baby not found")
    if baby.family_id != family_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Baby does not belong to family")

    family = db.get(Family, family_id)
    if family is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Family not found")

    actor = db.get(User, family.created_by_user_id)
    if actor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Actor not found")

    return baby, family, actor


# 返回 Agent 模块状态，便于确认模型配置和路由已经可用。
@router.get("/ping")
async def ping_agent_module() -> dict[str, str]:
    return {"module": "agent", "status": "ready"}


# 创建真实 Agent 会话，供问答和后续总结能力复用。
@router.post("/sessions", response_model=AgentSessionResponse)
async def create_agent_session(
    payload: CreateAgentSessionRequest,
    db: Session = Depends(get_db_session),
) -> AgentSessionResponse:
    baby, _, actor = resolve_agent_context(db=db, family_id=payload.family_id, baby_id=payload.baby_id)

    creator = db.get(User, payload.created_by_user_id)
    if creator is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Creator not found")

    session = AgentSession(
        id=str(uuid4()),
        family_id=payload.family_id,
        baby_id=payload.baby_id,
        created_by_user_id=payload.created_by_user_id,
        title=payload.title,
        status="active",
        last_message_at=None,
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return AgentSessionResponse(
        meta=build_agent_meta(user=actor, baby=baby, permissions=["agent:session:create", "agent:session:read"]),
        data=build_agent_session_data(session),
    )


# 返回指定宝宝的会话列表，供 Agent 页面展示历史会话。
@router.get("/sessions", response_model=AgentSessionListResponse)
async def list_agent_sessions(
    family_id: str = Query(..., description="家庭 ID"),
    baby_id: str = Query(..., description="宝宝 ID"),
    db: Session = Depends(get_db_session),
) -> AgentSessionListResponse:
    baby, _, actor = resolve_agent_context(db=db, family_id=family_id, baby_id=baby_id)
    sessions = db.scalars(
        select(AgentSession)
        .where(AgentSession.family_id == family_id, AgentSession.baby_id == baby_id)
        .order_by(AgentSession.updated_at.desc())
    ).all()

    return AgentSessionListResponse(
        meta=build_agent_meta(user=actor, baby=baby, permissions=["agent:session:read"]),
        data=[build_agent_session_data(session) for session in sessions],
    )


# 返回指定会话的消息列表，供前端恢复历史对话。
@router.get("/sessions/{session_id}/messages", response_model=AgentMessageListResponse)
async def list_agent_messages(
    session_id: str = Path(..., description="会话 ID"),
    db: Session = Depends(get_db_session),
) -> AgentMessageListResponse:
    session = db.get(AgentSession, session_id)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent session not found")

    baby, _, actor = resolve_agent_context(db=db, family_id=session.family_id, baby_id=session.baby_id)
    messages = db.scalars(
        select(AgentMessage)
        .where(AgentMessage.session_id == session_id)
        .order_by(AgentMessage.created_at.asc())
    ).all()

    return AgentMessageListResponse(
        meta=build_agent_meta(user=actor, baby=baby, permissions=["agent:message:read"]),
        data=[build_agent_message_data(message) for message in messages],
    )


# 向指定会话写入用户消息，并调用真实模型生成助手回复。
@router.post("/sessions/{session_id}/messages", response_model=CreateAgentMessageResponse)
async def create_agent_message(
    payload: CreateAgentMessageRequest,
    session_id: str = Path(..., description="会话 ID"),
    db: Session = Depends(get_db_session),
) -> CreateAgentMessageResponse:
    session = db.get(AgentSession, session_id)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent session not found")

    baby, _, actor = resolve_agent_context(db=db, family_id=session.family_id, baby_id=session.baby_id)

    user_message = AgentMessage(
        id=str(uuid4()),
        session_id=session.id,
        family_id=session.family_id,
        baby_id=session.baby_id,
        role="user",
        input_type=payload.input_type,
        content=payload.content,
        risk_level="low",
    )
    db.add(user_message)
    db.flush()

    try:
        assistant_content, risk_level = await generate_agent_reply(db=db, session=session, baby=baby)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Upstream model request failed: {exc.response.text}",
        ) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Upstream model request failed: {str(exc)}",
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc

    assistant_message = AgentMessage(
        id=str(uuid4()),
        session_id=session.id,
        family_id=session.family_id,
        baby_id=session.baby_id,
        role="assistant",
        input_type="text",
        content=assistant_content,
        risk_level=risk_level,
    )
    db.add(assistant_message)
    session.last_message_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user_message)
    db.refresh(assistant_message)
    db.refresh(session)

    return CreateAgentMessageResponse(
        meta=build_agent_meta(user=actor, baby=baby, permissions=["agent:message:write", "agent:message:read"]),
        data=[
            build_agent_message_data(user_message),
            build_agent_message_data(assistant_message),
        ],
    )
