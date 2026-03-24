from fastapi import APIRouter, Path

from app.api.placeholders import build_placeholder_meta
from app.schemas.baby_profile import (
    BabyProfileData,
    BabyProfileResponse,
    CreateBabyProfileRequest,
    SwitchCurrentBabyData,
    SwitchCurrentBabyRequest,
    SwitchCurrentBabyResponse,
    UpdateBabyProfileRequest,
)
from app.schemas.common import BabyContextMeta

router = APIRouter(prefix="/baby-profile", tags=["baby-profile"])


# 返回宝宝档案模块占位信息，用于确认模块路由注册成功。
@router.get("/ping")
async def ping_baby_profile_module() -> dict[str, str]:
    return {"module": "baby-profile", "status": "ready"}


# 创建宝宝档案占位记录，后续接入真实建档、家庭关联和默认当前宝宝逻辑。
@router.post("", response_model=BabyProfileResponse)
async def create_baby_profile(
    payload: CreateBabyProfileRequest,
) -> BabyProfileResponse:
    baby_context = BabyContextMeta(
        baby_id="baby_demo",
        baby_name=payload.nickname,
        age_days=0,
        age_months=0,
    )
    return BabyProfileResponse(
        meta=build_placeholder_meta(
            role="SuperOwner",
            baby_context=baby_context,
            permissions=["baby-profile:create", "baby-profile:read", "baby-profile:write"],
        ),
        data=BabyProfileData(
            baby_id="baby_demo",
            family_id="family_demo",
            nickname=payload.nickname,
            birth_date=payload.birth_date,
            birth_time=payload.birth_time,
            gender=payload.gender,
            birth_place=payload.birth_place,
            birth_height_cm=payload.birth_height_cm,
            birth_weight_kg=payload.birth_weight_kg,
            note=payload.note,
            is_current=True,
        ),
    )


# 返回当前宝宝档案占位信息，后续用于首页、成长记录和 Agent 上下文初始化。
@router.get("/current", response_model=BabyProfileResponse)
async def get_current_baby_profile() -> BabyProfileResponse:
    baby_context = BabyContextMeta(
        baby_id="baby_demo",
        baby_name="小宝宝",
        age_days=12,
        age_months=0,
    )
    return BabyProfileResponse(
        meta=build_placeholder_meta(
            role="SuperOwner",
            baby_context=baby_context,
            permissions=["baby-profile:read", "growth:read", "media:read"],
        ),
        data=BabyProfileData(
            baby_id="baby_demo",
            family_id="family_demo",
            nickname="小宝宝",
            birth_date="2026-03-12",
            birth_time="08:30",
            gender="female",
            birth_place="上海",
            birth_height_cm=50.0,
            birth_weight_kg=3.2,
            note="当前宝宝档案占位数据",
            is_current=True,
        ),
    )


# 更新指定宝宝档案占位信息，后续接入真实更新校验和审计逻辑。
@router.patch("/{baby_id}", response_model=BabyProfileResponse)
async def update_baby_profile(
    payload: UpdateBabyProfileRequest,
    baby_id: str = Path(..., description="宝宝 ID"),
) -> BabyProfileResponse:
    nickname = payload.nickname or "小宝宝"
    baby_context = BabyContextMeta(
        baby_id=baby_id,
        baby_name=nickname,
        age_days=12,
        age_months=0,
    )
    return BabyProfileResponse(
        meta=build_placeholder_meta(
            role="SuperOwner",
            baby_context=baby_context,
            permissions=["baby-profile:write", "baby-profile:read"],
        ),
        data=BabyProfileData(
            baby_id=baby_id,
            family_id="family_demo",
            nickname=nickname,
            birth_date="2026-03-12",
            birth_time="08:30",
            gender=payload.gender or "female",
            birth_place=payload.birth_place or "上海",
            birth_height_cm=payload.birth_height_cm or 50.0,
            birth_weight_kg=payload.birth_weight_kg or 3.2,
            note=payload.note or "更新后的宝宝档案占位数据",
            is_current=True,
        ),
    )


# 切换当前宝宝占位上下文，后续接入多宝宝场景下的家庭上下文切换逻辑。
@router.post("/switch", response_model=SwitchCurrentBabyResponse)
async def switch_current_baby(
    payload: SwitchCurrentBabyRequest,
) -> SwitchCurrentBabyResponse:
    baby_context = BabyContextMeta(
        baby_id=payload.baby_id,
        baby_name="切换后的宝宝",
        age_days=45,
        age_months=1,
    )
    return SwitchCurrentBabyResponse(
        meta=build_placeholder_meta(
            role="SuperOwner",
            baby_context=baby_context,
            permissions=["baby-profile:switch", "baby-profile:read"],
        ),
        data=SwitchCurrentBabyData(
            family_id="family_demo",
            current_baby=baby_context,
        ),
    )
