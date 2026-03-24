from datetime import date, datetime, timedelta, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.models.baby import Baby
from app.models.family import Family
from app.models.user import User
from app.models.vaccine import VaccinePlan, VaccineRecord
from app.schemas.common import ActorMeta, BabyContextMeta, ResponseMeta
from app.schemas.vaccine import (
    GenerateVaccinePlanRequest,
    RecordVaccineRequest,
    UpdateVaccineRecordRequest,
    VaccinePlanData,
    VaccinePlanListResponse,
    VaccineRecordData,
    VaccineRecordListResponse,
    VaccineRecordResponse,
)

router = APIRouter(prefix="/vaccine", tags=["vaccine"])

DEFAULT_VACCINE_TEMPLATES = [
    {"code": "hepb_1", "name": "乙肝疫苗", "dose_label": "第1剂", "offset_days": 0},
    {"code": "bcg_1", "name": "卡介苗", "dose_label": "第1剂", "offset_days": 1},
    {"code": "hepb_2", "name": "乙肝疫苗", "dose_label": "第2剂", "offset_days": 30},
]


# 构建疫苗模块统一响应元信息，附带当前操作者和宝宝上下文。
def build_vaccine_meta(user: User, baby: Baby, permissions: list[str]) -> ResponseMeta:
    age_days = max((date.today() - baby.birth_date).days, 0)
    return ResponseMeta(
        actor=ActorMeta(user_id=user.id, display_name=user.display_name, role="SuperOwner"),
        baby_context=BabyContextMeta(
            baby_id=baby.id,
            baby_name=baby.nickname,
            age_days=age_days,
            age_months=age_days // 30,
        ),
        timestamp=datetime.now(timezone.utc).isoformat(),
        permissions=permissions,
    )


# 将疫苗计划模型转换为统一响应结构。
def build_vaccine_plan_data(plan: VaccinePlan) -> VaccinePlanData:
    return VaccinePlanData(
        plan_id=plan.id,
        family_id=plan.family_id,
        baby_id=plan.baby_id,
        vaccine_code=plan.vaccine_code,
        vaccine_name=plan.vaccine_name,
        dose_label=plan.dose_label,
        scheduled_date=plan.scheduled_date.isoformat(),
        status=plan.status,
        notes=plan.notes,
        is_custom=plan.is_custom,
    )


# 将疫苗接种记录模型转换为统一响应结构。
def build_vaccine_record_data(record: VaccineRecord) -> VaccineRecordData:
    return VaccineRecordData(
        record_id=record.id,
        plan_id=record.plan_id,
        family_id=record.family_id,
        baby_id=record.baby_id,
        recorded_by_user_id=record.recorded_by_user_id,
        administered_date=record.administered_date.isoformat(),
        status=record.status,
        provider=record.provider,
        notes=record.notes,
    )


# 获取疫苗接口所需的宝宝、家庭和操作者上下文。
def resolve_vaccine_context(db: Session, family_id: str, baby_id: str) -> tuple[Baby, Family, User]:
    baby = db.get(Baby, baby_id)
    if baby is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Baby not found")
    if baby.family_id != family_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Baby does not belong to family")

    family = db.get(Family, family_id)
    if family is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Family not found")

    actor = db.get(User, family.created_by_user_id)
    if actor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Actor not found")

    return baby, family, actor


# 返回疫苗模块占位信息，用于确认模块路由注册成功。
@router.get("/ping")
async def ping_vaccine_module() -> dict[str, str]:
    return {"module": "vaccine", "status": "ready"}


# 为指定宝宝生成默认疫苗计划，当前仅生成一组最小基线数据。
@router.post("/plans/generate", response_model=VaccinePlanListResponse)
async def generate_vaccine_plans(
    payload: GenerateVaccinePlanRequest,
    db: Session = Depends(get_db_session),
) -> VaccinePlanListResponse:
    baby, _, actor = resolve_vaccine_context(db=db, family_id=payload.family_id, baby_id=payload.baby_id)

    existing_plans = db.scalars(
        select(VaccinePlan).where(VaccinePlan.family_id == payload.family_id, VaccinePlan.baby_id == payload.baby_id)
    ).all()
    if not existing_plans:
        for template in DEFAULT_VACCINE_TEMPLATES:
            plan = VaccinePlan(
                id=str(uuid4()),
                family_id=payload.family_id,
                baby_id=payload.baby_id,
                vaccine_code=template["code"],
                vaccine_name=template["name"],
                dose_label=template["dose_label"],
                scheduled_date=baby.birth_date + timedelta(days=template["offset_days"]),
                status="pending",
                notes=None,
                is_custom=False,
            )
            db.add(plan)
        db.commit()

    plans = db.scalars(
        select(VaccinePlan)
        .where(VaccinePlan.family_id == payload.family_id, VaccinePlan.baby_id == payload.baby_id)
        .order_by(VaccinePlan.scheduled_date.asc())
    ).all()

    return VaccinePlanListResponse(
        meta=build_vaccine_meta(user=actor, baby=baby, permissions=["vaccine:plan:write", "vaccine:plan:read"]),
        data=[build_vaccine_plan_data(plan) for plan in plans],
    )


# 返回指定宝宝的疫苗计划列表，供疫苗页面和首页待办使用。
@router.get("/plans", response_model=VaccinePlanListResponse)
async def list_vaccine_plans(
    family_id: str = Query(..., description="家庭 ID"),
    baby_id: str = Query(..., description="宝宝 ID"),
    db: Session = Depends(get_db_session),
) -> VaccinePlanListResponse:
    baby, _, actor = resolve_vaccine_context(db=db, family_id=family_id, baby_id=baby_id)
    plans = db.scalars(
        select(VaccinePlan)
        .where(VaccinePlan.family_id == family_id, VaccinePlan.baby_id == baby_id)
        .order_by(VaccinePlan.scheduled_date.asc())
    ).all()

    return VaccinePlanListResponse(
        meta=build_vaccine_meta(user=actor, baby=baby, permissions=["vaccine:plan:read"]),
        data=[build_vaccine_plan_data(plan) for plan in plans],
    )


# 记录真实接种结果，并同步更新对应疫苗计划状态。
@router.post("/records", response_model=VaccineRecordResponse)
async def create_vaccine_record(
    payload: RecordVaccineRequest,
    db: Session = Depends(get_db_session),
) -> VaccineRecordResponse:
    plan = db.get(VaccinePlan, payload.plan_id)
    if plan is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vaccine plan not found")

    baby, _, actor = resolve_vaccine_context(db=db, family_id=plan.family_id, baby_id=plan.baby_id)
    recorder = db.get(User, payload.recorded_by_user_id)
    if recorder is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recorder not found")

    record = VaccineRecord(
        id=str(uuid4()),
        plan_id=plan.id,
        family_id=plan.family_id,
        baby_id=plan.baby_id,
        recorded_by_user_id=payload.recorded_by_user_id,
        administered_date=date.fromisoformat(payload.administered_date),
        status=payload.status,
        provider=payload.provider,
        notes=payload.notes,
    )
    db.add(record)
    plan.status = "completed" if payload.status == "completed" else "delayed"
    db.commit()
    db.refresh(record)

    return VaccineRecordResponse(
        meta=build_vaccine_meta(user=actor, baby=baby, permissions=["vaccine:record:write", "vaccine:record:read"]),
        data=build_vaccine_record_data(record),
    )


# 返回指定宝宝的接种记录列表，供疫苗页查看历史接种结果。
@router.get("/records", response_model=VaccineRecordListResponse)
async def list_vaccine_records(
    family_id: str = Query(..., description="家庭 ID"),
    baby_id: str = Query(..., description="宝宝 ID"),
    db: Session = Depends(get_db_session),
) -> VaccineRecordListResponse:
    baby, _, actor = resolve_vaccine_context(db=db, family_id=family_id, baby_id=baby_id)
    records = db.scalars(
        select(VaccineRecord)
        .where(VaccineRecord.family_id == family_id, VaccineRecord.baby_id == baby_id)
        .order_by(VaccineRecord.administered_date.desc())
    ).all()

    return VaccineRecordListResponse(
        meta=build_vaccine_meta(user=actor, baby=baby, permissions=["vaccine:record:read"]),
        data=[build_vaccine_record_data(record) for record in records],
    )


# 更新接种记录状态和备注，并同步回写对应疫苗计划状态。
@router.patch("/records/{record_id}", response_model=VaccineRecordResponse)
async def update_vaccine_record(
    payload: UpdateVaccineRecordRequest,
    record_id: str = Path(..., description="接种记录 ID"),
    db: Session = Depends(get_db_session),
) -> VaccineRecordResponse:
    record = db.get(VaccineRecord, record_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vaccine record not found")

    baby, _, actor = resolve_vaccine_context(db=db, family_id=record.family_id, baby_id=record.baby_id)
    plan = db.get(VaccinePlan, record.plan_id)
    if plan is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vaccine plan not found")

    record.status = payload.status
    record.provider = payload.provider
    record.notes = payload.notes
    plan.status = "completed" if payload.status == "completed" else "delayed"
    db.commit()
    db.refresh(record)

    return VaccineRecordResponse(
        meta=build_vaccine_meta(user=actor, baby=baby, permissions=["vaccine:record:write", "vaccine:record:read"]),
        data=build_vaccine_record_data(record),
    )
