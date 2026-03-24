from datetime import date, datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.models.baby import Baby
from app.models.family import Family
from app.models.user import User
from app.schemas.baby_profile import (
    BabyProfileData,
    BabyProfileResponse,
    CreateBabyProfileRequest,
    SwitchCurrentBabyData,
    SwitchCurrentBabyRequest,
    SwitchCurrentBabyResponse,
    UpdateBabyProfileRequest,
)
from app.schemas.common import ActorMeta, BabyContextMeta, ResponseMeta

router = APIRouter(prefix="/baby-profile", tags=["baby-profile"])


# 计算宝宝当前日龄和月龄，用于首页和 Agent 上下文展示。
def build_baby_context(baby: Baby) -> BabyContextMeta:
    today = date.today()
    age_days = max((today - baby.birth_date).days, 0)
    age_months = age_days // 30
    return BabyContextMeta(
        baby_id=baby.id,
        baby_name=baby.nickname,
        age_days=age_days,
        age_months=age_months,
    )


# 构建宝宝档案模块统一响应元信息，附带当前操作者和宝宝上下文。
def build_baby_profile_meta(user: User, baby: Baby, permissions: list[str]) -> ResponseMeta:
    return ResponseMeta(
        actor=ActorMeta(user_id=user.id, display_name=user.display_name, role="SuperOwner"),
        baby_context=build_baby_context(baby),
        timestamp=datetime.now(timezone.utc).isoformat(),
        permissions=permissions,
    )


# 将宝宝模型转换为统一的档案响应数据。
def build_baby_profile_data(baby: Baby, family: Family) -> BabyProfileData:
    return BabyProfileData(
        baby_id=baby.id,
        family_id=family.id,
        nickname=baby.nickname,
        birth_date=baby.birth_date.isoformat(),
        birth_time=baby.birth_time,
        gender=baby.gender,
        birth_place=baby.birth_place,
        birth_height_cm=baby.birth_height_cm,
        birth_weight_kg=baby.birth_weight_kg,
        note=baby.note,
        is_current=family.current_baby_id == baby.id,
    )


# 获取目标家庭并校验存在性，供宝宝档案接口统一复用。
def resolve_family(db: Session, family_id: str) -> Family:
    family = db.get(Family, family_id)
    if family is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Family not found")
    return family


# 获取家庭创建者作为当前操作者，供宝宝档案接口统一返回元信息。
def resolve_family_actor(db: Session, family: Family) -> User:
    actor = db.get(User, family.created_by_user_id)
    if actor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Actor not found")
    return actor


# 返回宝宝档案模块占位信息，用于确认模块路由注册成功。
@router.get("/ping")
async def ping_baby_profile_module() -> dict[str, str]:
    return {"module": "baby-profile", "status": "ready"}


# 创建宝宝档案并在没有当前宝宝时自动设为当前宝宝。
@router.post("", response_model=BabyProfileResponse)
async def create_baby_profile(
    payload: CreateBabyProfileRequest,
    db: Session = Depends(get_db_session),
) -> BabyProfileResponse:
    family = resolve_family(db=db, family_id=payload.family_id)
    actor = resolve_family_actor(db=db, family=family)

    baby = Baby(
        id=str(uuid4()),
        family_id=family.id,
        nickname=payload.nickname,
        birth_date=date.fromisoformat(payload.birth_date),
        birth_time=payload.birth_time,
        gender=payload.gender,
        birth_place=payload.birth_place,
        birth_height_cm=payload.birth_height_cm,
        birth_weight_kg=payload.birth_weight_kg,
        note=payload.note,
    )
    db.add(baby)
    db.flush()

    if family.current_baby_id is None:
        family.current_baby_id = baby.id

    db.commit()
    db.refresh(baby)
    db.refresh(family)

    return BabyProfileResponse(
        meta=build_baby_profile_meta(
            user=actor,
            baby=baby,
            permissions=["baby-profile:create", "baby-profile:read", "baby-profile:write"],
        ),
        data=build_baby_profile_data(baby=baby, family=family),
    )


# 返回当前宝宝档案真实数据，默认读取家庭当前选中的宝宝。
@router.get("/current", response_model=BabyProfileResponse)
async def get_current_baby_profile(
    family_id: str = Query(..., description="家庭 ID"),
    db: Session = Depends(get_db_session),
) -> BabyProfileResponse:
    family = resolve_family(db=db, family_id=family_id)
    actor = resolve_family_actor(db=db, family=family)
    if family.current_baby_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Current baby not set")

    baby = db.get(Baby, family.current_baby_id)
    if baby is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Baby not found")

    return BabyProfileResponse(
        meta=build_baby_profile_meta(
            user=actor,
            baby=baby,
            permissions=["baby-profile:read", "growth:read", "media:read"],
        ),
        data=build_baby_profile_data(baby=baby, family=family),
    )


# 更新指定宝宝档案，并返回更新后的真实档案数据。
@router.patch("/{baby_id}", response_model=BabyProfileResponse)
async def update_baby_profile(
    payload: UpdateBabyProfileRequest,
    baby_id: str = Path(..., description="宝宝 ID"),
    db: Session = Depends(get_db_session),
) -> BabyProfileResponse:
    baby = db.get(Baby, baby_id)
    if baby is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Baby not found")

    family = resolve_family(db=db, family_id=baby.family_id)
    actor = resolve_family_actor(db=db, family=family)

    if payload.nickname is not None:
        baby.nickname = payload.nickname
    if payload.birth_time is not None:
        baby.birth_time = payload.birth_time
    if payload.gender is not None:
        baby.gender = payload.gender
    if payload.birth_place is not None:
        baby.birth_place = payload.birth_place
    if payload.birth_height_cm is not None:
        baby.birth_height_cm = payload.birth_height_cm
    if payload.birth_weight_kg is not None:
        baby.birth_weight_kg = payload.birth_weight_kg
    if payload.note is not None:
        baby.note = payload.note

    db.commit()
    db.refresh(baby)

    return BabyProfileResponse(
        meta=build_baby_profile_meta(
            user=actor,
            baby=baby,
            permissions=["baby-profile:write", "baby-profile:read"],
        ),
        data=build_baby_profile_data(baby=baby, family=family),
    )


# 切换家庭当前宝宝，供多宝宝场景和首页上下文切换使用。
@router.post("/switch", response_model=SwitchCurrentBabyResponse)
async def switch_current_baby(
    payload: SwitchCurrentBabyRequest,
    db: Session = Depends(get_db_session),
) -> SwitchCurrentBabyResponse:
    family = resolve_family(db=db, family_id=payload.family_id)
    actor = resolve_family_actor(db=db, family=family)

    baby = db.scalar(
        select(Baby).where(Baby.id == payload.baby_id, Baby.family_id == family.id)
    )
    if baby is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Baby not found")

    family.current_baby_id = baby.id
    db.commit()

    baby_context = build_baby_context(baby)
    return SwitchCurrentBabyResponse(
        meta=ResponseMeta(
            actor=ActorMeta(user_id=actor.id, display_name=actor.display_name, role="SuperOwner"),
            baby_context=baby_context,
            timestamp=datetime.now(timezone.utc).isoformat(),
            permissions=["baby-profile:switch", "baby-profile:read"],
        ),
        data=SwitchCurrentBabyData(
            family_id=family.id,
            current_baby=baby_context,
        ),
    )
