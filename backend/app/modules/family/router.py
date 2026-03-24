from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.models.family import Family, FamilyMember
from app.models.user import User
from app.schemas.common import ActorMeta, ResponseMeta, RoleName
from app.schemas.family import (
    CreateFamilyRequest,
    FamilyData,
    FamilyMemberData,
    FamilyMembersResponse,
    FamilyResponse,
    UpdateFamilyMemberRoleRequest,
    UpdateFamilyMemberRoleResponse,
)

router = APIRouter(prefix="/family", tags=["family"])


# 构建家庭模块响应元信息，统一携带当前操作者和权限信息。
def build_family_meta(user: User, role: RoleName, permissions: list[str]) -> ResponseMeta:
    return ResponseMeta(
        actor=ActorMeta(user_id=user.id, display_name=user.display_name, role=role),
        baby_context=None,
        timestamp=datetime.now(timezone.utc).isoformat(),
        permissions=permissions,
    )


# 将家庭模型和成员数量转换为统一的家庭响应数据。
def build_family_data(family: Family, member_count: int) -> FamilyData:
    return FamilyData(
        family_id=family.id,
        name=family.name,
        description=family.description,
        member_count=member_count,
        current_baby_id=family.current_baby_id,
    )


# 将家庭成员模型和用户模型组合成成员响应数据。
def build_family_member_data(member: FamilyMember, user: User) -> FamilyMemberData:
    return FamilyMemberData(
        member_id=member.id,
        user_id=user.id,
        display_name=user.display_name,
        role=member.role,
        status=member.status,
    )


# 获取目标家庭，不传 family_id 时默认返回最早创建的家庭。
def resolve_family(db: Session, family_id: str | None) -> Family:
    if family_id:
        family = db.get(Family, family_id)
    else:
        family = db.scalar(select(Family).order_by(Family.created_at.asc()))

    if family is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Family not found")
    return family


# 返回家庭模块占位信息，用于确认模块路由注册成功。
@router.get("/ping")
async def ping_family_module() -> dict[str, str]:
    return {"module": "family", "status": "ready"}


# 创建家庭、创建者用户以及默认 SuperOwner 成员关系。
@router.post("", response_model=FamilyResponse)
async def create_family(
    payload: CreateFamilyRequest,
    db: Session = Depends(get_db_session),
) -> FamilyResponse:
    creator = db.scalar(select(User).where(User.email == payload.creator_email))
    if creator is None:
        creator = User(
            id=str(uuid4()),
            email=payload.creator_email,
            display_name=payload.creator_display_name,
            status="active",
        )
        db.add(creator)
        db.flush()

    family = Family(
        id=str(uuid4()),
        name=payload.name,
        description=payload.description,
        created_by_user_id=creator.id,
        current_baby_id=None,
    )
    db.add(family)
    db.flush()

    family_member = FamilyMember(
        id=str(uuid4()),
        family_id=family.id,
        user_id=creator.id,
        role="SuperOwner",
        status="active",
    )
    db.add(family_member)
    db.commit()
    db.refresh(family)

    return FamilyResponse(
        meta=build_family_meta(
            user=creator,
            role="SuperOwner",
            permissions=["family:create", "family:read", "family:write"],
        ),
        data=build_family_data(family=family, member_count=1),
    )


# 返回当前家庭空间真实数据，默认取数据库中的首个家庭记录。
@router.get("/current", response_model=FamilyResponse)
async def get_current_family(
    family_id: str | None = Query(default=None, description="家庭 ID，可选"),
    db: Session = Depends(get_db_session),
) -> FamilyResponse:
    family = resolve_family(db=db, family_id=family_id)
    creator = db.get(User, family.created_by_user_id)
    if creator is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Creator not found")

    member_count = db.scalar(
        select(func.count()).select_from(FamilyMember).where(FamilyMember.family_id == family.id)
    ) or 0

    return FamilyResponse(
        meta=build_family_meta(
            user=creator,
            role="SuperOwner",
            permissions=["family:read", "family:write"],
        ),
        data=build_family_data(family=family, member_count=member_count),
    )


# 返回当前家庭的成员列表真实数据，默认取数据库中的首个家庭记录。
@router.get("/members", response_model=FamilyMembersResponse)
async def list_family_members(
    family_id: str | None = Query(default=None, description="家庭 ID，可选"),
    db: Session = Depends(get_db_session),
) -> FamilyMembersResponse:
    family = resolve_family(db=db, family_id=family_id)
    creator = db.get(User, family.created_by_user_id)
    if creator is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Creator not found")

    member_rows = db.execute(
        select(FamilyMember, User)
        .join(User, User.id == FamilyMember.user_id)
        .where(FamilyMember.family_id == family.id)
        .order_by(FamilyMember.created_at.asc())
    ).all()

    return FamilyMembersResponse(
        meta=build_family_meta(
            user=creator,
            role="SuperOwner",
            permissions=["family:read", "family:member:read", "family:member:write"],
        ),
        data=[build_family_member_data(member=member, user=user) for member, user in member_rows],
    )


# 更新家庭成员角色，当前先限制不能直接通过该接口修改 SuperOwner。
@router.patch("/members/{member_id}/role", response_model=UpdateFamilyMemberRoleResponse)
async def update_family_member_role(
    payload: UpdateFamilyMemberRoleRequest,
    member_id: str = Path(..., description="家庭成员 ID"),
    db: Session = Depends(get_db_session),
) -> UpdateFamilyMemberRoleResponse:
    member = db.get(FamilyMember, member_id)
    if member is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Family member not found")
    if member.role == "SuperOwner":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SuperOwner role cannot be changed here",
        )

    member.role = payload.role
    db.commit()
    db.refresh(member)

    user = db.get(User, member.user_id)
    family = db.get(Family, member.family_id)
    if user is None or family is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Related data not found")

    actor = db.get(User, family.created_by_user_id)
    if actor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Actor not found")

    return UpdateFamilyMemberRoleResponse(
        meta=build_family_meta(
            user=actor,
            role="SuperOwner",
            permissions=["family:member:write"],
        ),
        data=build_family_member_data(member=member, user=user),
    )
