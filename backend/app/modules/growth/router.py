from fastapi import APIRouter, Query

from app.api.placeholders import build_placeholder_meta
from app.schemas.common import BabyContextMeta
from app.schemas.growth import (
    CreateGrowthRecordRequest,
    GrowthAssessmentData,
    GrowthAssessmentResponse,
    GrowthRecordData,
    GrowthRecordListResponse,
    GrowthRecordResponse,
    GrowthRecordType,
    GrowthTrendData,
    GrowthTrendPoint,
    GrowthTrendResponse,
)

router = APIRouter(prefix="/growth", tags=["growth"])


# 返回成长记录模块占位信息，用于确认模块路由注册成功。
@router.get("/ping")
async def ping_growth_module() -> dict[str, str]:
    return {"module": "growth", "status": "ready"}


# 创建成长记录占位数据，后续接入真实落库、权限校验和自动评估逻辑。
@router.post("", response_model=GrowthRecordResponse)
async def create_growth_record(
    payload: CreateGrowthRecordRequest,
) -> GrowthRecordResponse:
    baby_context = BabyContextMeta(
        baby_id=payload.baby_id,
        baby_name="小宝宝",
        age_days=12,
        age_months=0,
    )
    return GrowthRecordResponse(
        meta=build_placeholder_meta(
            role="Editor",
            display_name="宝宝妈妈",
            baby_context=baby_context,
            permissions=["growth:create", "growth:read"],
        ),
        data=GrowthRecordData(
            record_id="growth_record_001",
            baby_id=payload.baby_id,
            record_type=payload.record_type,
            value=payload.value,
            unit=payload.unit,
            recorded_at=payload.recorded_at,
            note=payload.note,
            age_days=12,
            age_months=0,
        ),
    )


# 返回成长记录列表占位数据，后续用于成长页列表和时间轴聚合展示。
@router.get("", response_model=GrowthRecordListResponse)
async def list_growth_records(
    baby_id: str = Query(..., description="宝宝 ID"),
    record_type: GrowthRecordType | None = Query(default=None, description="记录类型过滤"),
) -> GrowthRecordListResponse:
    selected_type = record_type or "weight"
    baby_context = BabyContextMeta(
        baby_id=baby_id,
        baby_name="小宝宝",
        age_days=12,
        age_months=0,
    )
    unit = "kg" if selected_type == "weight" else "cm"
    return GrowthRecordListResponse(
        meta=build_placeholder_meta(
            role="SuperOwner",
            baby_context=baby_context,
            permissions=["growth:read"],
        ),
        data=[
            GrowthRecordData(
                record_id="growth_record_001",
                baby_id=baby_id,
                record_type=selected_type,
                value=3.2 if selected_type == "weight" else 50.0,
                unit=unit,
                recorded_at="2026-03-12T08:30:00+08:00",
                note="出生记录",
                age_days=0,
                age_months=0,
            ),
            GrowthRecordData(
                record_id="growth_record_002",
                baby_id=baby_id,
                record_type=selected_type,
                value=3.6 if selected_type == "weight" else 52.0,
                unit=unit,
                recorded_at="2026-03-24T09:00:00+08:00",
                note="近一次记录",
                age_days=12,
                age_months=0,
            ),
        ],
    )


# 返回最近一条成长记录占位数据，后续用于首页摘要和 Agent 上下文拼装。
@router.get("/latest", response_model=GrowthRecordResponse)
async def get_latest_growth_record(
    baby_id: str = Query(..., description="宝宝 ID"),
    record_type: GrowthRecordType = Query(..., description="记录类型"),
) -> GrowthRecordResponse:
    baby_context = BabyContextMeta(
        baby_id=baby_id,
        baby_name="小宝宝",
        age_days=12,
        age_months=0,
    )
    unit = "kg" if record_type == "weight" else "cm"
    value = 3.6 if record_type == "weight" else 52.0
    return GrowthRecordResponse(
        meta=build_placeholder_meta(
            role="SuperOwner",
            baby_context=baby_context,
            permissions=["growth:read"],
        ),
        data=GrowthRecordData(
            record_id="growth_record_latest",
            baby_id=baby_id,
            record_type=record_type,
            value=value,
            unit=unit,
            recorded_at="2026-03-24T09:00:00+08:00",
            note="最近一次记录",
            age_days=12,
            age_months=0,
        ),
    )


# 返回成长趋势占位数据，后续用于趋势图和周报分析。
@router.get("/trends", response_model=GrowthTrendResponse)
async def get_growth_trends(
    baby_id: str = Query(..., description="宝宝 ID"),
    record_type: GrowthRecordType = Query(..., description="记录类型"),
) -> GrowthTrendResponse:
    baby_context = BabyContextMeta(
        baby_id=baby_id,
        baby_name="小宝宝",
        age_days=12,
        age_months=0,
    )
    unit = "kg" if record_type == "weight" else "cm"
    return GrowthTrendResponse(
        meta=build_placeholder_meta(
            role="SuperOwner",
            baby_context=baby_context,
            permissions=["growth:read", "growth:trend:read"],
        ),
        data=GrowthTrendData(
            baby_id=baby_id,
            record_type=record_type,
            points=[
                GrowthTrendPoint(
                    recorded_at="2026-03-12T08:30:00+08:00",
                    value=3.2 if record_type == "weight" else 50.0,
                    unit=unit,
                    age_days=0,
                ),
                GrowthTrendPoint(
                    recorded_at="2026-03-18T09:00:00+08:00",
                    value=3.4 if record_type == "weight" else 51.2,
                    unit=unit,
                    age_days=6,
                ),
                GrowthTrendPoint(
                    recorded_at="2026-03-24T09:00:00+08:00",
                    value=3.6 if record_type == "weight" else 52.0,
                    unit=unit,
                    age_days=12,
                ),
            ],
        ),
    )


# 返回最新成长评估占位数据，后续接入百分位、BMI 和建议生成逻辑。
@router.get("/assessments/latest", response_model=GrowthAssessmentResponse)
async def get_latest_growth_assessment(
    baby_id: str = Query(..., description="宝宝 ID"),
    record_type: GrowthRecordType = Query(..., description="记录类型"),
) -> GrowthAssessmentResponse:
    baby_context = BabyContextMeta(
        baby_id=baby_id,
        baby_name="小宝宝",
        age_days=12,
        age_months=0,
    )
    return GrowthAssessmentResponse(
        meta=build_placeholder_meta(
            role="SuperOwner",
            baby_context=baby_context,
            permissions=["growth:read", "growth:assessment:read"],
        ),
        data=GrowthAssessmentData(
            baby_id=baby_id,
            record_type=record_type,
            age_days=12,
            age_months=0,
            percentile=58.0,
            bmi=14.3 if record_type == "weight" else None,
            status="normal",
            advice="当前记录处于正常范围，建议继续按周观察变化趋势。",
        ),
    )
