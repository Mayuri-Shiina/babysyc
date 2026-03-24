from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.common import ResponseMeta

ReminderType = Literal["vaccine", "checkup", "missing_record", "milestone", "agent_followup"]
ReminderStatus = Literal["pending", "done", "cancelled"]


class CreateReminderRequest(BaseModel):
    family_id: str = Field(..., description="家庭 ID")
    baby_id: str = Field(..., description="宝宝 ID")
    created_by_user_id: str = Field(..., description="创建者用户 ID")
    reminder_type: ReminderType = Field(..., description="提醒类型")
    title: str = Field(..., description="提醒标题")
    description: str | None = Field(default=None, description="提醒描述")
    due_at: str = Field(..., description="提醒时间，ISO 格式时间字符串")
    source: str | None = Field(default=None, description="提醒来源")


class ReminderData(BaseModel):
    reminder_id: str
    family_id: str
    baby_id: str
    created_by_user_id: str
    reminder_type: ReminderType
    title: str
    description: str | None = None
    due_at: str
    status: ReminderStatus
    source: str | None = None


class ReminderResponse(BaseModel):
    meta: ResponseMeta
    data: ReminderData


class ReminderListResponse(BaseModel):
    meta: ResponseMeta
    data: list[ReminderData]


class ConfirmReminderRequest(BaseModel):
    status: Literal["done", "cancelled"] = Field(..., description="确认后的提醒状态")


class ConfirmReminderResponse(BaseModel):
    meta: ResponseMeta
    data: ReminderData
