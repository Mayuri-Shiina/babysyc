from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.common import EditableRoleName, ResponseMeta, RoleName

InvitationStatus = Literal["pending", "accepted", "expired"]


class LoginRequest(BaseModel):
    email: str = Field(..., description="登录邮箱")
    invite_code: str | None = Field(default=None, description="邀请码，占位字段")


class SessionData(BaseModel):
    user_id: str
    display_name: str
    email: str
    role: RoleName
    family_id: str | None = None


class LoginResponse(BaseModel):
    meta: ResponseMeta
    data: SessionData


class CreateInvitationRequest(BaseModel):
    invitee_name: str = Field(..., description="被邀请人姓名或称呼")
    invitee_email: str = Field(..., description="被邀请人邮箱")
    role: EditableRoleName = Field(..., description="被邀请人的家庭角色")
    note: str | None = Field(default=None, description="邀请备注")


class InvitationData(BaseModel):
    invitation_id: str
    invitee_name: str
    invitee_email: str
    role: EditableRoleName
    status: InvitationStatus
    invite_token: str


class InvitationResponse(BaseModel):
    meta: ResponseMeta
    data: InvitationData


class AcceptInvitationRequest(BaseModel):
    invite_token: str = Field(..., description="邀请令牌")
    display_name: str = Field(..., description="接受邀请后的展示名称")


class AcceptInvitationData(BaseModel):
    user_id: str
    family_id: str
    role: EditableRoleName
    status: Literal["accepted"]


class AcceptInvitationResponse(BaseModel):
    meta: ResponseMeta
    data: AcceptInvitationData


class SessionResponse(BaseModel):
    meta: ResponseMeta
    data: SessionData
