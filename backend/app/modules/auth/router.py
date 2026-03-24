from fastapi import APIRouter

from app.api.placeholders import build_placeholder_meta
from app.schemas.auth import (
    AcceptInvitationData,
    AcceptInvitationRequest,
    AcceptInvitationResponse,
    CreateInvitationRequest,
    InvitationData,
    InvitationResponse,
    LoginRequest,
    LoginResponse,
    SessionData,
    SessionResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


# 返回认证模块占位信息，用于确认模块路由注册成功。
@router.get("/ping")
async def ping_auth_module() -> dict[str, str]:
    return {"module": "auth", "status": "ready"}


# 接收登录请求并返回当前会话占位信息，后续接入真实登录和会话生成逻辑。
@router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest) -> LoginResponse:
    return LoginResponse(
        meta=build_placeholder_meta(
            role="SuperOwner",
            permissions=["auth:login", "family:read", "family:write"],
        ),
        data=SessionData(
            user_id="user_super_owner",
            display_name="SuperOwner",
            email=payload.email,
            role="SuperOwner",
            family_id="family_demo",
        ),
    )


# 创建邀请占位记录，后续接入真实邀请落库和通知发送逻辑。
@router.post("/invitations", response_model=InvitationResponse)
async def create_invitation(payload: CreateInvitationRequest) -> InvitationResponse:
    return InvitationResponse(
        meta=build_placeholder_meta(
            role="SuperOwner",
            permissions=["auth:invite:create", "family:member:write"],
        ),
        data=InvitationData(
            invitation_id="invite_001",
            invitee_name=payload.invitee_name,
            invitee_email=payload.invitee_email,
            role=payload.role,
            status="pending",
            invite_token="invite_token_placeholder",
        ),
    )


# 接收邀请令牌并返回接受邀请后的会话占位结果。
@router.post("/invitations/accept", response_model=AcceptInvitationResponse)
async def accept_invitation(
    payload: AcceptInvitationRequest,
) -> AcceptInvitationResponse:
    return AcceptInvitationResponse(
        meta=build_placeholder_meta(
            role="Editor",
            display_name=payload.display_name,
            permissions=["family:read", "growth:write", "media:write"],
        ),
        data=AcceptInvitationData(
            user_id="user_editor_001",
            family_id="family_demo",
            role="Editor",
            status="accepted",
        ),
    )


# 返回当前登录用户的会话占位信息，后续用于前端恢复身份和权限状态。
@router.get("/session", response_model=SessionResponse)
async def get_current_session() -> SessionResponse:
    return SessionResponse(
        meta=build_placeholder_meta(
            role="SuperOwner",
            permissions=["auth:read", "family:read", "family:write"],
        ),
        data=SessionData(
            user_id="user_super_owner",
            display_name="SuperOwner",
            email="superowner@example.com",
            role="SuperOwner",
            family_id="family_demo",
        ),
    )
