from datetime import datetime, timezone

from app.schemas.common import BabyContextMeta, ActorMeta, ResponseMeta, RoleName


# 生成统一的占位响应元信息，便于接口在业务实现前保持返回结构一致。
def build_placeholder_meta(
    role: RoleName = "SuperOwner",
    display_name: str = "SuperOwner",
    baby_context: BabyContextMeta | None = None,
    permissions: list[str] | None = None,
) -> ResponseMeta:
    return ResponseMeta(
        actor=ActorMeta(
            user_id="user_placeholder",
            display_name=display_name,
            role=role,
        ),
        baby_context=baby_context,
        timestamp=datetime.now(timezone.utc).isoformat(),
        permissions=permissions or [],
    )
