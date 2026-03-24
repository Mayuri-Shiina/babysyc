from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.common import ResponseMeta

GrowthRecordType = Literal[
    "height",
    "weight",
    "head_circumference",
    "temperature",
    "sleep",
    "feeding",
]
AssessmentStatus = Literal["low", "normal", "high", "observe"]


class CreateGrowthRecordRequest(BaseModel):
    baby_id: str = Field(..., description="宝宝 ID")
    record_type: GrowthRecordType = Field(..., description="记录类型")
    value: float = Field(..., description="记录值")
    unit: str = Field(..., description="记录单位")
    recorded_at: str = Field(..., description="记录时间，ISO 格式时间字符串")
    note: str | None = Field(default=None, description="备注信息")


class GrowthRecordData(BaseModel):
    record_id: str
    baby_id: str
    record_type: GrowthRecordType
    value: float
    unit: str
    recorded_at: str
    note: str | None = None
    age_days: int
    age_months: int


class GrowthRecordResponse(BaseModel):
    meta: ResponseMeta
    data: GrowthRecordData


class GrowthRecordListResponse(BaseModel):
    meta: ResponseMeta
    data: list[GrowthRecordData]


class GrowthTrendPoint(BaseModel):
    recorded_at: str
    value: float
    unit: str
    age_days: int


class GrowthTrendData(BaseModel):
    baby_id: str
    record_type: GrowthRecordType
    points: list[GrowthTrendPoint]


class GrowthTrendResponse(BaseModel):
    meta: ResponseMeta
    data: GrowthTrendData


class GrowthAssessmentData(BaseModel):
    baby_id: str
    record_type: GrowthRecordType
    age_days: int
    age_months: int
    percentile: float | None = None
    bmi: float | None = None
    status: AssessmentStatus
    advice: str


class GrowthAssessmentResponse(BaseModel):
    meta: ResponseMeta
    data: GrowthAssessmentData
