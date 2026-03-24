from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.common import ResponseMeta

AgentSessionStatus = Literal["active", "archived"]
AgentMessageRole = Literal["user", "assistant"]
AgentInputType = Literal["text", "image", "voice"]
RiskLevel = Literal["low", "medium", "high"]
AgentSummaryType = Literal["weekly", "monthly"]
AgentSuggestionPriority = Literal["low", "medium", "high"]
AgentSuggestionKind = Literal[
    "missing_growth_record",
    "missing_media_description",
    "age_based_prompt",
    "pending_reminder",
]


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


class GenerateAgentSummaryRequest(BaseModel):
    family_id: str = Field(..., description="家庭 ID")
    baby_id: str = Field(..., description="宝宝 ID")
    generated_by_user_id: str = Field(..., description="生成人用户 ID")
    anchor_date: date | None = Field(default=None, description="统计锚点日期，默认今天")


class AgentSummaryData(BaseModel):
    summary_id: str
    family_id: str
    baby_id: str
    generated_by_user_id: str
    summary_type: AgentSummaryType
    period_start: str
    period_end: str
    title: str
    content: str
    key_points: list[str] = Field(default_factory=list)
    created_at: str


class AgentSummaryResponse(BaseModel):
    meta: ResponseMeta
    data: AgentSummaryData


class AgentSummaryListResponse(BaseModel):
    meta: ResponseMeta
    data: list[AgentSummaryData]


class AgentSuggestionData(BaseModel):
    suggestion_id: str
    kind: AgentSuggestionKind
    title: str
    content: str
    reason: str
    priority: AgentSuggestionPriority


class AgentSuggestionListResponse(BaseModel):
    meta: ResponseMeta
    data: list[AgentSuggestionData]
