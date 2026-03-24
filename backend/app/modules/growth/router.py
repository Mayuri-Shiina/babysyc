from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.models.baby import Baby
from app.models.family import Family
from app.models.growth import GrowthRecord
from app.models.user import User
from app.schemas.common import ActorMeta, BabyContextMeta, ResponseMeta
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


# 根据宝宝出生日期和记录时间计算日龄与月龄。
def calculate_age_metrics(baby: Baby, recorded_at: datetime) -> tuple[int, int]:
    age_days = max((recorded_at.date() - baby.birth_date).days, 0)
    return age_days, age_days // 30


# 构建成长模块统一响应元信息，附带当前宝宝上下文和操作者信息。
def build_growth_meta(user: User, baby: Baby, permissions: list[str]) -> ResponseMeta:
    now = datetime.now(timezone.utc).isoformat()
    current_age_days = max((datetime.now().date() - baby.birth_date).days, 0)
    return ResponseMeta(
        actor=ActorMeta(user_id=user.id, display_name=user.display_name, role="SuperOwner"),
        baby_context=BabyContextMeta(
            baby_id=baby.id,
            baby_name=baby.nickname,
            age_days=current_age_days,
            age_months=current_age_days // 30,
        ),
        timestamp=now,
        permissions=permissions,
    )


# 将成长记录模型转换为统一响应结构。
def build_growth_record_data(record: GrowthRecord, baby: Baby) -> GrowthRecordData:
    age_days, age_months = calculate_age_metrics(baby=baby, recorded_at=record.recorded_at)
    return GrowthRecordData(
        record_id=record.id,
        baby_id=record.baby_id,
        record_type=record.record_type,
        value=record.value,
        unit=record.unit,
        recorded_at=record.recorded_at.isoformat(),
        note=record.note,
        age_days=age_days,
        age_months=age_months,
    )


# 获取指定宝宝及其所属家庭、操作者信息，供成长接口统一复用。
def resolve_growth_context(db: Session, baby_id: str) -> tuple[Baby, Family, User]:
    baby = db.get(Baby, baby_id)
    if baby is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Baby not found")

    family = db.get(Family, baby.family_id)
    if family is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Family not found")

    actor = db.get(User, family.created_by_user_id)
    if actor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Actor not found")

    return baby, family, actor


# 根据最新记录生成轻量评估结果，后续可替换为更完整的百分位算法。
def build_growth_assessment(record: GrowthRecord, baby: Baby) -> GrowthAssessmentData:
    age_days, age_months = calculate_age_metrics(baby=baby, recorded_at=record.recorded_at)
    status_value = "normal"
    advice = "当前记录处于正常范围，建议继续按周观察变化趋势。"
    percentile = 58.0

    if record.record_type == "weight" and record.value < 2.5:
        status_value = "low"
        advice = "体重偏低，建议复测并结合喂养情况持续观察。"
        percentile = 12.0
    elif record.record_type == "weight" and record.value > 8.0:
        status_value = "high"
        advice = "体重偏高，建议结合月龄与近期趋势继续观察。"
        percentile = 88.0

    bmi = None
    if record.record_type == "weight" and baby.birth_height_cm:
        height_m = baby.birth_height_cm / 100
        if height_m > 0:
            bmi = round(record.value / (height_m * height_m), 2)

    return GrowthAssessmentData(
        baby_id=baby.id,
        record_type=record.record_type,
        age_days=age_days,
        age_months=age_months,
        percentile=percentile,
        bmi=bmi,
        status=status_value,
        advice=advice,
    )


# 返回成长记录模块占位信息，用于确认模块路由注册成功。
@router.get("/ping")
async def ping_growth_module() -> dict[str, str]:
    return {"module": "growth", "status": "ready"}


# 创建真实成长记录并返回落库后的记录结果。
@router.post("", response_model=GrowthRecordResponse)
async def create_growth_record(
    payload: CreateGrowthRecordRequest,
    db: Session = Depends(get_db_session),
) -> GrowthRecordResponse:
    baby, _, actor = resolve_growth_context(db=db, baby_id=payload.baby_id)
    recorded_at = datetime.fromisoformat(payload.recorded_at)
    if recorded_at.tzinfo is None:
        recorded_at = recorded_at.replace(tzinfo=timezone.utc)

    record = GrowthRecord(
        id=str(uuid4()),
        baby_id=payload.baby_id,
        record_type=payload.record_type,
        value=payload.value,
        unit=payload.unit,
        recorded_at=recorded_at,
        note=payload.note,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return GrowthRecordResponse(
        meta=build_growth_meta(
            user=actor,
            baby=baby,
            permissions=["growth:create", "growth:read"],
        ),
        data=build_growth_record_data(record=record, baby=baby),
    )


# 返回宝宝的真实成长记录列表，并支持按记录类型筛选。
@router.get("", response_model=GrowthRecordListResponse)
async def list_growth_records(
    baby_id: str = Query(..., description="宝宝 ID"),
    record_type: GrowthRecordType | None = Query(default=None, description="记录类型过滤"),
    db: Session = Depends(get_db_session),
) -> GrowthRecordListResponse:
    baby, _, actor = resolve_growth_context(db=db, baby_id=baby_id)

    query = select(GrowthRecord).where(GrowthRecord.baby_id == baby_id)
    if record_type is not None:
        query = query.where(GrowthRecord.record_type == record_type)
    query = query.order_by(GrowthRecord.recorded_at.asc())

    records = db.scalars(query).all()
    return GrowthRecordListResponse(
        meta=build_growth_meta(user=actor, baby=baby, permissions=["growth:read"]),
        data=[build_growth_record_data(record=record, baby=baby) for record in records],
    )


# 返回指定类型的最近一条真实成长记录，供首页摘要和 Agent 使用。
@router.get("/latest", response_model=GrowthRecordResponse)
async def get_latest_growth_record(
    baby_id: str = Query(..., description="宝宝 ID"),
    record_type: GrowthRecordType = Query(..., description="记录类型"),
    db: Session = Depends(get_db_session),
) -> GrowthRecordResponse:
    baby, _, actor = resolve_growth_context(db=db, baby_id=baby_id)
    record = db.scalar(
        select(GrowthRecord)
        .where(GrowthRecord.baby_id == baby_id, GrowthRecord.record_type == record_type)
        .order_by(GrowthRecord.recorded_at.desc())
    )
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Growth record not found")

    return GrowthRecordResponse(
        meta=build_growth_meta(user=actor, baby=baby, permissions=["growth:read"]),
        data=build_growth_record_data(record=record, baby=baby),
    )


# 返回指定类型的真实成长趋势点，供趋势图和总结使用。
@router.get("/trends", response_model=GrowthTrendResponse)
async def get_growth_trends(
    baby_id: str = Query(..., description="宝宝 ID"),
    record_type: GrowthRecordType = Query(..., description="记录类型"),
    db: Session = Depends(get_db_session),
) -> GrowthTrendResponse:
    baby, _, actor = resolve_growth_context(db=db, baby_id=baby_id)
    records = db.scalars(
        select(GrowthRecord)
        .where(GrowthRecord.baby_id == baby_id, GrowthRecord.record_type == record_type)
        .order_by(GrowthRecord.recorded_at.asc())
    ).all()

    points = []
    for record in records:
        age_days, _ = calculate_age_metrics(baby=baby, recorded_at=record.recorded_at)
        points.append(
            GrowthTrendPoint(
                recorded_at=record.recorded_at.isoformat(),
                value=record.value,
                unit=record.unit,
                age_days=age_days,
            )
        )

    return GrowthTrendResponse(
        meta=build_growth_meta(
            user=actor,
            baby=baby,
            permissions=["growth:read", "growth:trend:read"],
        ),
        data=GrowthTrendData(
            baby_id=baby_id,
            record_type=record_type,
            points=points,
        ),
    )


# 返回指定类型最新记录的轻量评估结果，供首页和 Agent 使用。
@router.get("/assessments/latest", response_model=GrowthAssessmentResponse)
async def get_latest_growth_assessment(
    baby_id: str = Query(..., description="宝宝 ID"),
    record_type: GrowthRecordType = Query(..., description="记录类型"),
    db: Session = Depends(get_db_session),
) -> GrowthAssessmentResponse:
    baby, _, actor = resolve_growth_context(db=db, baby_id=baby_id)
    record = db.scalar(
        select(GrowthRecord)
        .where(GrowthRecord.baby_id == baby_id, GrowthRecord.record_type == record_type)
        .order_by(GrowthRecord.recorded_at.desc())
    )
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Growth record not found")

    return GrowthAssessmentResponse(
        meta=build_growth_meta(
            user=actor,
            baby=baby,
            permissions=["growth:read", "growth:assessment:read"],
        ),
        data=build_growth_assessment(record=record, baby=baby),
    )
