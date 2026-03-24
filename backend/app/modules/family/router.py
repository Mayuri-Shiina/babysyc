from fastapi import APIRouter, Path

from app.api.placeholders import build_placeholder_meta
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


# 返回家庭模块占位信息，用于确认模块路由注册成功。
@router.get("/ping")
async def ping_family_module() -> dict[str, str]:
    return {"module": "family", "status": "ready"}


# 创建家庭空间占位记录，后续接入真实家庭初始化和默认成员创建逻辑。
@router.post("", response_model=FamilyResponse)
async def create_family(payload: CreateFamilyRequest) -> FamilyResponse:
    return FamilyResponse(
        meta=build_placeholder_meta(
            role="SuperOwner",
            permissions=["family:create", "family:read", "family:write"],
        ),
        data=FamilyData(
            family_id="family_demo",
            name=payload.name,
            description=payload.description,
            member_count=1,
            current_baby_id=None,
        ),
    )


# 返回当前家庭空间占位信息，后续用于首页初始化和家庭上下文切换。
@router.get("/current", response_model=FamilyResponse)
async def get_current_family() -> FamilyResponse:
    return FamilyResponse(
        meta=build_placeholder_meta(
            role="SuperOwner",
            permissions=["family:read", "family:write"],
        ),
        data=FamilyData(
            family_id="family_demo",
            name="宝宝成长档案家庭",
            description="当前家庭空间占位数据",
            member_count=3,
            current_baby_id="baby_demo",
        ),
    )


# 返回当前家庭成员列表占位数据，后续用于成员管理和权限展示。
@router.get("/members", response_model=FamilyMembersResponse)
async def list_family_members() -> FamilyMembersResponse:
    return FamilyMembersResponse(
        meta=build_placeholder_meta(
            role="SuperOwner",
            permissions=["family:read", "family:member:read", "family:member:write"],
        ),
        data=[
            FamilyMemberData(
                member_id="member_001",
                user_id="user_super_owner",
                display_name="SuperOwner",
                role="SuperOwner",
                status="active",
            ),
            FamilyMemberData(
                member_id="member_002",
                user_id="user_editor_001",
                display_name="宝宝妈妈",
                role="Editor",
                status="active",
            ),
            FamilyMemberData(
                member_id="member_003",
                user_id="user_viewer_001",
                display_name="分享访客",
                role="Viewer",
                status="active",
            ),
        ],
    )


# 更新指定家庭成员的角色占位信息，后续接入真实权限校验和成员更新逻辑。
@router.patch("/members/{member_id}/role", response_model=UpdateFamilyMemberRoleResponse)
async def update_family_member_role(
    payload: UpdateFamilyMemberRoleRequest,
    member_id: str = Path(..., description="家庭成员 ID"),
) -> UpdateFamilyMemberRoleResponse:
    return UpdateFamilyMemberRoleResponse(
        meta=build_placeholder_meta(
            role="SuperOwner",
            permissions=["family:member:write"],
        ),
        data=FamilyMemberData(
            member_id=member_id,
            user_id="user_target_member",
            display_name="目标家庭成员",
            role=payload.role,
            status="active",
        ),
    )
