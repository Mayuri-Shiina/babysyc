from typing import Literal

from pydantic import BaseModel, Field

RoleName = Literal["SuperOwner", "Editor", "Viewer", "Anonymous"]
EditableRoleName = Literal["Editor", "Viewer"]


class ActorMeta(BaseModel):
    user_id: str
    display_name: str
    role: RoleName


class BabyContextMeta(BaseModel):
    baby_id: str | None = None
    baby_name: str | None = None
    age_days: int | None = None
    age_months: int | None = None


class ResponseMeta(BaseModel):
    actor: ActorMeta
    baby_context: BabyContextMeta | None = None
    timestamp: str
    permissions: list[str] = Field(default_factory=list)
