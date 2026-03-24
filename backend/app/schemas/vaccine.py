from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.common import ResponseMeta

VaccinePlanStatus = Literal["pending", "completed", "delayed", "cancelled"]
VaccineRecordStatus = Literal["completed", "delayed", "contraindicated"]


class GenerateVaccinePlanRequest(BaseModel):
    family_id: str = Field(..., description="家庭 ID")
    baby_id: str = Field(..., description="宝宝 ID")


class VaccinePlanData(BaseModel):
    plan_id: str
    family_id: str
    baby_id: str
    vaccine_code: str
    vaccine_name: str
    dose_label: str
    scheduled_date: str
    status: VaccinePlanStatus
    notes: str | None = None
    is_custom: bool


class VaccinePlanListResponse(BaseModel):
    meta: ResponseMeta
    data: list[VaccinePlanData]


class RecordVaccineRequest(BaseModel):
    plan_id: str = Field(..., description="疫苗计划 ID")
    recorded_by_user_id: str = Field(..., description="记录人用户 ID")
    administered_date: str = Field(..., description="接种日期，ISO 格式日期字符串")
    status: VaccineRecordStatus = Field(default="completed", description="接种状态")
    provider: str | None = Field(default=None, description="接种机构")
    notes: str | None = Field(default=None, description="接种备注")


class UpdateVaccineRecordRequest(BaseModel):
    status: VaccineRecordStatus = Field(..., description="接种状态")
    provider: str | None = Field(default=None, description="接种机构")
    notes: str | None = Field(default=None, description="接种备注")


class VaccineRecordData(BaseModel):
    record_id: str
    plan_id: str
    family_id: str
    baby_id: str
    recorded_by_user_id: str
    administered_date: str
    status: VaccineRecordStatus
    provider: str | None = None
    notes: str | None = None


class VaccineRecordResponse(BaseModel):
    meta: ResponseMeta
    data: VaccineRecordData


class VaccineRecordListResponse(BaseModel):
    meta: ResponseMeta
    data: list[VaccineRecordData]
