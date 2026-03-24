from datetime import datetime, timezone
from secrets import token_urlsafe
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.models.family import Family, FamilyInvitation, FamilyMember
from app.models.user import User
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
from app.schemas.common import ActorMeta, ResponseMeta, RoleName

router = APIRouter(prefix="/auth", tags=["auth"])


# 构建认证模块响应元信息，统一携带当前操作者和权限信息。
def build_auth_meta(user: User, role: RoleName, permissions: list[str]) -> ResponseMeta:
    return ResponseMeta(
        actor=ActorMeta(user_id=user.id, display_name=user.display_name, role=role),
        baby_context=None,
        timestamp=datetime.now(timezone.utc).isoformat(),
        permissions=permissions,
    )


# 将用户和家庭成员关系转换为统一的会话响应数据。
def build_session_data(user: User, family_member: FamilyMember | None) -> SessionData:
    return SessionData(
        user_id=user.id,
        display_name=user.display_name,
        email=user.email,
        role=family_member.role if family_member else "Anonymous",
        family_id=family_member.family_id if family_member else None,
    )


# 返回认证模块占位信息，用于确认模块路由注册成功。
@router.get("/ping")
async def ping_auth_module() -> dict[str, str]:
    return {"module": "auth", "status": "ready"}


# 按邮箱读取真实用户和家庭成员关系，返回当前会话结构。
@router.post("/login", response_model=LoginResponse)
async def login(
    payload: LoginRequest,
    db: Session = Depends(get_db_session),
) -> LoginResponse:
    user = db.scalar(select(User).where(User.email == payload.email))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    family_member = db.scalar(
        select(FamilyMember)
        .where(FamilyMember.user_id == user.id)
        .order_by(FamilyMember.created_at.asc())
    )
    role: RoleName = family_member.role if family_member else "Anonymous"
    permissions = ["auth:login", "family:read"]
    if role in {"SuperOwner", "Editor"}:
        permissions.append("family:write")

    return LoginResponse(
        meta=build_auth_meta(user=user, role=role, permissions=permissions),
        data=build_session_data(user=user, family_member=family_member),
    )


# 创建家庭邀请记录并保存到数据库，供后续接受邀请流程使用。
@router.post("/invitations", response_model=InvitationResponse)
async def create_invitation(
    payload: CreateInvitationRequest,
    db: Session = Depends(get_db_session),
) -> InvitationResponse:
    family = db.get(Family, payload.family_id)
    if family is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Family not found")

    inviter = db.get(User, family.created_by_user_id)
    if inviter is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inviter not found")

    invitation = FamilyInvitation(
        id=str(uuid4()),
        family_id=family.id,
        invited_by_user_id=inviter.id,
        invitee_name=payload.invitee_name,
        invitee_email=payload.invitee_email,
        role=payload.role,
        status="pending",
        invite_token=token_urlsafe(24),
        note=payload.note,
    )
    db.add(invitation)
    db.commit()
    db.refresh(invitation)

    return InvitationResponse(
        meta=build_auth_meta(
            user=inviter,
            role="SuperOwner",
            permissions=["auth:invite:create", "family:member:write"],
        ),
        data=InvitationData(
            invitation_id=invitation.id,
            family_id=invitation.family_id,
            invitee_name=invitation.invitee_name,
            invitee_email=invitation.invitee_email,
            role=invitation.role,
            status=invitation.status,
            invite_token=invitation.invite_token,
        ),
    )


# 接受家庭邀请并创建真实家庭成员关系，必要时自动创建用户。
@router.post("/invitations/accept", response_model=AcceptInvitationResponse)
async def accept_invitation(
    payload: AcceptInvitationRequest,
    db: Session = Depends(get_db_session),
) -> AcceptInvitationResponse:
    invitation = db.scalar(
        select(FamilyInvitation).where(FamilyInvitation.invite_token == payload.invite_token)
    )
    if invitation is None or invitation.status != "pending":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found")

    user = db.scalar(select(User).where(User.email == invitation.invitee_email))
    if user is None:
        user = User(
            id=str(uuid4()),
            email=invitation.invitee_email,
            display_name=payload.display_name,
            status="active",
        )
        db.add(user)
        db.flush()

    family_member = db.scalar(
        select(FamilyMember).where(
            FamilyMember.family_id == invitation.family_id,
            FamilyMember.user_id == user.id,
        )
    )
    if family_member is None:
        family_member = FamilyMember(
            id=str(uuid4()),
            family_id=invitation.family_id,
            user_id=user.id,
            role=invitation.role,
            status="active",
        )
        db.add(family_member)

    invitation.status = "accepted"
    invitation.accepted_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    db.refresh(family_member)

    return AcceptInvitationResponse(
        meta=build_auth_meta(
            user=user,
            role=family_member.role,
            permissions=["family:read", "growth:write", "media:write"],
        ),
        data=AcceptInvitationData(
            user_id=user.id,
            family_id=family_member.family_id,
            role=family_member.role,
            status="accepted",
        ),
    )


# 返回当前数据库中的首个有效会话数据，作为临时会话查询实现。
@router.get("/session", response_model=SessionResponse)
async def get_current_session(
    db: Session = Depends(get_db_session),
) -> SessionResponse:
    family_member = db.scalar(select(FamilyMember).order_by(FamilyMember.created_at.asc()))
    if family_member is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active session data")

    user = db.get(User, family_member.user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    permissions = ["auth:read", "family:read"]
    if family_member.role in {"SuperOwner", "Editor"}:
        permissions.append("family:write")

    return SessionResponse(
        meta=build_auth_meta(user=user, role=family_member.role, permissions=permissions),
        data=build_session_data(user=user, family_member=family_member),
    )
