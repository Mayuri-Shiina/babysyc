from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.common import ResponseMeta

AgentSessionStatus = Literal["active", "archived"]
AgentMessageRole = Literal["user", "assistant"]
AgentInputType = Literal["text", "image", "voice"]
RiskLevel = Literal["low", "medium", "high"]


class CreateAgentSessionRequest(BaseModel):
    family_id: str = Field(..., description="家庭 ID")
    baby_id: str = Field(..., description="宝宝 ID")
    created_by_user_id: str = Field(..., description="创建者用户 ID")
    title: str = Field(..., description="会话标题")


class AgentSessionData(BaseModel):
    session_id: str
    family_id: str
    baby_id: str
    created_by_user_id: str
    title: str
    status: AgentSessionStatus
    last_message_at: str | None = None


class AgentSessionResponse(BaseModel):
    meta: ResponseMeta
    data: AgentSessionData


class AgentSessionListResponse(BaseModel):
    meta: ResponseMeta
    data: list[AgentSessionData]


class CreateAgentMessageRequest(BaseModel):
    content: str = Field(..., description="用户消息内容")
    input_type: AgentInputType = Field(default="text", description="输入类型")


class AgentMessageData(BaseModel):
    message_id: str
    session_id: str
    family_id: str
    baby_id: str
    role: AgentMessageRole
    input_type: AgentInputType
    content: str
    risk_level: RiskLevel
    created_at: str


class AgentMessageListResponse(BaseModel):
    meta: ResponseMeta
    data: list[AgentMessageData]


class CreateAgentMessageResponse(BaseModel):
    meta: ResponseMeta
    data: list[AgentMessageData]
