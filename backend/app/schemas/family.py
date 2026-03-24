from pydantic import BaseModel, Field

from app.schemas.common import EditableRoleName, ResponseMeta, RoleName


class CreateFamilyRequest(BaseModel):
    name: str = Field(..., description="家庭名称")
    description: str | None = Field(default=None, description="家庭简介")


class FamilyData(BaseModel):
    family_id: str
    name: str
    description: str | None = None
    member_count: int
    current_baby_id: str | None = None


class FamilyResponse(BaseModel):
    meta: ResponseMeta
    data: FamilyData


class FamilyMemberData(BaseModel):
    member_id: str
    user_id: str
    display_name: str
    role: RoleName
    status: str


class FamilyMembersResponse(BaseModel):
    meta: ResponseMeta
    data: list[FamilyMemberData]


class UpdateFamilyMemberRoleRequest(BaseModel):
    role: EditableRoleName = Field(..., description="新的家庭角色")


class UpdateFamilyMemberRoleResponse(BaseModel):
    meta: ResponseMeta
    data: FamilyMemberData
