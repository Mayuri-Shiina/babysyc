from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.models.baby import Baby
from app.models.family import Family
from app.models.media import MediaAsset
from app.models.user import User
from app.schemas.common import ActorMeta, BabyContextMeta, ResponseMeta
from app.schemas.media import (
    CreateMediaAssetRequest,
    MediaAssetData,
    MediaAssetListResponse,
    MediaAssetResponse,
    MediaType,
)

router = APIRouter(prefix="/media", tags=["media"])


# 构建媒体模块统一响应元信息，附带当前操作者和宝宝上下文。
def build_media_meta(user: User, baby: Baby, permissions: list[str]) -> ResponseMeta:
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


# 将媒体模型转换为统一响应结构。
def build_media_asset_data(asset: MediaAsset) -> MediaAssetData:
    tags = asset.tags.split(",") if asset.tags else []
    return MediaAssetData(
        media_id=asset.id,
        family_id=asset.family_id,
        baby_id=asset.baby_id,
        uploaded_by_user_id=asset.uploaded_by_user_id,
        media_type=asset.media_type,
        file_name=asset.file_name,
        file_url=asset.file_url,
        thumbnail_url=asset.thumbnail_url,
        mime_type=asset.mime_type,
        description=asset.description,
        tags=[tag for tag in tags if tag],
        captured_at=asset.captured_at.isoformat(),
        visibility=asset.visibility,
    )


# 获取媒体接口所需的宝宝、家庭和操作者上下文。
def resolve_media_context(db: Session, baby_id: str, family_id: str) -> tuple[Baby, Family, User]:
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


# 返回媒体模块占位信息，用于确认模块路由注册成功。
@router.get("/ping")
async def ping_media_module() -> dict[str, str]:
    return {"module": "media", "status": "ready"}


# 创建真实媒体元数据记录，供后续时间轴和相册页查询使用。
@router.post("", response_model=MediaAssetResponse)
async def create_media_asset(
    payload: CreateMediaAssetRequest,
    db: Session = Depends(get_db_session),
) -> MediaAssetResponse:
    baby, _, actor = resolve_media_context(db=db, baby_id=payload.baby_id, family_id=payload.family_id)

    uploader = db.get(User, payload.uploaded_by_user_id)
    if uploader is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Uploader not found")

    captured_at = datetime.fromisoformat(payload.captured_at)
    if captured_at.tzinfo is None:
        captured_at = captured_at.replace(tzinfo=timezone.utc)

    asset = MediaAsset(
        id=str(uuid4()),
        family_id=payload.family_id,
        baby_id=payload.baby_id,
        uploaded_by_user_id=payload.uploaded_by_user_id,
        media_type=payload.media_type,
        file_name=payload.file_name,
        file_url=payload.file_url,
        thumbnail_url=payload.thumbnail_url,
        mime_type=payload.mime_type,
        description=payload.description,
        tags=",".join(payload.tags),
        captured_at=captured_at,
        visibility=payload.visibility,
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)

    return MediaAssetResponse(
        meta=build_media_meta(
            user=actor,
            baby=baby,
            permissions=["media:create", "media:read"],
        ),
        data=build_media_asset_data(asset),
    )


# 返回指定宝宝的媒体列表，支持按媒体类型和月份过滤。
@router.get("", response_model=MediaAssetListResponse)
async def list_media_assets(
    family_id: str = Query(..., description="家庭 ID"),
    baby_id: str = Query(..., description="宝宝 ID"),
    media_type: MediaType | None = Query(default=None, description="媒体类型过滤"),
    month: str | None = Query(default=None, description="按 YYYY-MM 过滤"),
    db: Session = Depends(get_db_session),
) -> MediaAssetListResponse:
    baby, _, actor = resolve_media_context(db=db, baby_id=baby_id, family_id=family_id)

    query = select(MediaAsset).where(MediaAsset.family_id == family_id, MediaAsset.baby_id == baby_id)
    if media_type is not None:
        query = query.where(MediaAsset.media_type == media_type)

    assets = db.scalars(query.order_by(MediaAsset.captured_at.desc())).all()
    if month is not None:
        assets = [asset for asset in assets if asset.captured_at.strftime("%Y-%m") == month]

    return MediaAssetListResponse(
        meta=build_media_meta(user=actor, baby=baby, permissions=["media:read"]),
        data=[build_media_asset_data(asset) for asset in assets],
    )


# 返回时间轴排序的媒体列表，供首页和时间轴页直接复用。
@router.get("/timeline", response_model=MediaAssetListResponse)
async def list_media_timeline(
    family_id: str = Query(..., description="家庭 ID"),
    baby_id: str = Query(..., description="宝宝 ID"),
    db: Session = Depends(get_db_session),
) -> MediaAssetListResponse:
    baby, _, actor = resolve_media_context(db=db, baby_id=baby_id, family_id=family_id)
    assets = db.scalars(
        select(MediaAsset)
        .where(MediaAsset.family_id == family_id, MediaAsset.baby_id == baby_id)
        .order_by(MediaAsset.captured_at.desc())
    ).all()

    return MediaAssetListResponse(
        meta=build_media_meta(user=actor, baby=baby, permissions=["media:read", "media:timeline:read"]),
        data=[build_media_asset_data(asset) for asset in assets],
    )


# 返回最近一条媒体记录，供首页最近照片和最近视频区域复用。
@router.get("/latest", response_model=MediaAssetResponse)
async def get_latest_media_asset(
    family_id: str = Query(..., description="家庭 ID"),
    baby_id: str = Query(..., description="宝宝 ID"),
    media_type: MediaType | None = Query(default=None, description="媒体类型过滤"),
    db: Session = Depends(get_db_session),
) -> MediaAssetResponse:
    baby, _, actor = resolve_media_context(db=db, baby_id=baby_id, family_id=family_id)

    query = select(MediaAsset).where(MediaAsset.family_id == family_id, MediaAsset.baby_id == baby_id)
    if media_type is not None:
        query = query.where(MediaAsset.media_type == media_type)
    asset = db.scalar(query.order_by(MediaAsset.captured_at.desc()))
    if asset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media asset not found")

    return MediaAssetResponse(
        meta=build_media_meta(user=actor, baby=baby, permissions=["media:read"]),
        data=build_media_asset_data(asset),
    )
