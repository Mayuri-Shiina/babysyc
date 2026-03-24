from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.models.baby import Baby
from app.models.family import Family
from app.models.reminder import Reminder
from app.models.user import User
from app.schemas.common import ActorMeta, BabyContextMeta, ResponseMeta
from app.schemas.reminder import (
    ConfirmReminderRequest,
    ConfirmReminderResponse,
    CreateReminderRequest,
    ReminderData,
    ReminderListResponse,
    ReminderResponse,
    ReminderStatus,
    ReminderType,
)

router = APIRouter(prefix="/reminder", tags=["reminder"])


# 构建提醒模块统一响应元信息，附带当前操作者和宝宝上下文。
def build_reminder_meta(user: User, baby: Baby, permissions: list[str]) -> ResponseMeta:
    age_days = max((datetime.now().date() - baby.birth_date).days, 0)
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


# 将提醒模型转换为统一响应结构。
def build_reminder_data(reminder: Reminder) -> ReminderData:
    return ReminderData(
        reminder_id=reminder.id,
        family_id=reminder.family_id,
        baby_id=reminder.baby_id,
        created_by_user_id=reminder.created_by_user_id,
        reminder_type=reminder.reminder_type,
        title=reminder.title,
        description=reminder.description,
        due_at=reminder.due_at.isoformat(),
        status=reminder.status,
        source=reminder.source,
    )


# 获取提醒接口所需的宝宝、家庭和操作者上下文。
def resolve_reminder_context(db: Session, family_id: str, baby_id: str) -> tuple[Baby, Family, User]:
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


# 返回提醒模块占位信息，用于确认模块路由注册成功。
@router.get("/ping")
async def ping_reminder_module() -> dict[str, str]:
    return {"module": "reminder", "status": "ready"}


# 创建真实提醒记录，供首页待提醒和记录引导使用。
@router.post("", response_model=ReminderResponse)
async def create_reminder(
    payload: CreateReminderRequest,
    db: Session = Depends(get_db_session),
) -> ReminderResponse:
    baby, _, actor = resolve_reminder_context(
        db=db,
        family_id=payload.family_id,
        baby_id=payload.baby_id,
    )

    creator = db.get(User, payload.created_by_user_id)
    if creator is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Creator not found")

    due_at = datetime.fromisoformat(payload.due_at)
    if due_at.tzinfo is None:
        due_at = due_at.replace(tzinfo=timezone.utc)

    reminder = Reminder(
        id=str(uuid4()),
        family_id=payload.family_id,
        baby_id=payload.baby_id,
        created_by_user_id=payload.created_by_user_id,
        reminder_type=payload.reminder_type,
        title=payload.title,
        description=payload.description,
        due_at=due_at,
        status="pending",
        source=payload.source,
    )
    db.add(reminder)
    db.commit()
    db.refresh(reminder)

    return ReminderResponse(
        meta=build_reminder_meta(user=actor, baby=baby, permissions=["reminder:create", "reminder:read"]),
        data=build_reminder_data(reminder),
    )


# 返回指定宝宝的提醒列表，支持按状态和类型过滤。
@router.get("", response_model=ReminderListResponse)
async def list_reminders(
    family_id: str = Query(..., description="家庭 ID"),
    baby_id: str = Query(..., description="宝宝 ID"),
    status_filter: ReminderStatus | None = Query(default=None, alias="status", description="提醒状态过滤"),
    reminder_type: ReminderType | None = Query(default=None, description="提醒类型过滤"),
    db: Session = Depends(get_db_session),
) -> ReminderListResponse:
    baby, _, actor = resolve_reminder_context(db=db, family_id=family_id, baby_id=baby_id)

    query = select(Reminder).where(Reminder.family_id == family_id, Reminder.baby_id == baby_id)
    if status_filter is not None:
        query = query.where(Reminder.status == status_filter)
    if reminder_type is not None:
        query = query.where(Reminder.reminder_type == reminder_type)

    reminders = db.scalars(query.order_by(Reminder.due_at.asc())).all()
    return ReminderListResponse(
        meta=build_reminder_meta(user=actor, baby=baby, permissions=["reminder:read"]),
        data=[build_reminder_data(reminder) for reminder in reminders],
    )


# 返回近期待处理提醒，供首页待提醒区域直接使用。
@router.get("/upcoming", response_model=ReminderListResponse)
async def list_upcoming_reminders(
    family_id: str = Query(..., description="家庭 ID"),
    baby_id: str = Query(..., description="宝宝 ID"),
    limit: int = Query(default=5, ge=1, le=20, description="返回数量限制"),
    db: Session = Depends(get_db_session),
) -> ReminderListResponse:
    baby, _, actor = resolve_reminder_context(db=db, family_id=family_id, baby_id=baby_id)
    reminders = db.scalars(
        select(Reminder)
        .where(
            Reminder.family_id == family_id,
            Reminder.baby_id == baby_id,
            Reminder.status == "pending",
        )
        .order_by(Reminder.due_at.asc())
        .limit(limit)
    ).all()

    return ReminderListResponse(
        meta=build_reminder_meta(user=actor, baby=baby, permissions=["reminder:read", "reminder:upcoming:read"]),
        data=[build_reminder_data(reminder) for reminder in reminders],
    )


# 确认提醒已完成或取消，供首页和提醒中心更新状态。
@router.patch("/{reminder_id}/confirm", response_model=ConfirmReminderResponse)
async def confirm_reminder(
    payload: ConfirmReminderRequest,
    reminder_id: str = Path(..., description="提醒 ID"),
    db: Session = Depends(get_db_session),
) -> ConfirmReminderResponse:
    reminder = db.get(Reminder, reminder_id)
    if reminder is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found")

    baby, _, actor = resolve_reminder_context(
        db=db,
        family_id=reminder.family_id,
        baby_id=reminder.baby_id,
    )
    reminder.status = payload.status
    db.commit()
    db.refresh(reminder)

    return ConfirmReminderResponse(
        meta=build_reminder_meta(user=actor, baby=baby, permissions=["reminder:write", "reminder:read"]),
        data=build_reminder_data(reminder),
    )
