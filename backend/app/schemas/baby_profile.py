from pydantic import BaseModel, Field

from app.schemas.common import BabyContextMeta, ResponseMeta


class CreateBabyProfileRequest(BaseModel):
    family_id: str = Field(..., description="家庭 ID")
    nickname: str = Field(..., description="宝宝昵称")
    birth_date: str = Field(..., description="出生日期，ISO 格式日期字符串")
    birth_time: str | None = Field(default=None, description="出生时间，HH:MM 格式")
    gender: str = Field(..., description="宝宝性别")
    birth_place: str | None = Field(default=None, description="出生地点")
    birth_height_cm: float | None = Field(default=None, description="出生身高，单位厘米")
    birth_weight_kg: float | None = Field(default=None, description="出生体重，单位千克")
    note: str | None = Field(default=None, description="备注信息")


class UpdateBabyProfileRequest(BaseModel):
    nickname: str | None = Field(default=None, description="宝宝昵称")
    birth_time: str | None = Field(default=None, description="出生时间，HH:MM 格式")
    gender: str | None = Field(default=None, description="宝宝性别")
    birth_place: str | None = Field(default=None, description="出生地点")
    birth_height_cm: float | None = Field(default=None, description="出生身高，单位厘米")
    birth_weight_kg: float | None = Field(default=None, description="出生体重，单位千克")
    note: str | None = Field(default=None, description="备注信息")


class SwitchCurrentBabyRequest(BaseModel):
    family_id: str = Field(..., description="家庭 ID")
    baby_id: str = Field(..., description="目标宝宝 ID")


class BabyProfileData(BaseModel):
    baby_id: str
    family_id: str
    nickname: str
    birth_date: str
    birth_time: str | None = None
    gender: str
    birth_place: str | None = None
    birth_height_cm: float | None = None
    birth_weight_kg: float | None = None
    note: str | None = None
    is_current: bool


class BabyProfileResponse(BaseModel):
    meta: ResponseMeta
    data: BabyProfileData


class SwitchCurrentBabyData(BaseModel):
    family_id: str
    current_baby: BabyContextMeta


class SwitchCurrentBabyResponse(BaseModel):
    meta: ResponseMeta
    data: SwitchCurrentBabyData
