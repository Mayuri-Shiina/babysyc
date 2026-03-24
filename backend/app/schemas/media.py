from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.common import ResponseMeta

MediaType = Literal["image", "video"]
VisibilityType = Literal["family", "viewer"]


class CreateMediaAssetRequest(BaseModel):
    family_id: str = Field(..., description="家庭 ID")
    baby_id: str = Field(..., description="宝宝 ID")
    uploaded_by_user_id: str = Field(..., description="上传者用户 ID")
    media_type: MediaType = Field(..., description="媒体类型")
    file_name: str = Field(..., description="文件名")
    file_url: str = Field(..., description="文件访问地址")
    thumbnail_url: str | None = Field(default=None, description="缩略图地址")
    mime_type: str | None = Field(default=None, description="媒体 MIME 类型")
    description: str | None = Field(default=None, description="媒体描述")
    tags: list[str] = Field(default_factory=list, description="媒体标签列表")
    captured_at: str = Field(..., description="拍摄或记录时间，ISO 格式时间字符串")
    visibility: VisibilityType = Field(default="family", description="可见范围")


class MediaAssetData(BaseModel):
    media_id: str
    family_id: str
    baby_id: str
    uploaded_by_user_id: str
    media_type: MediaType
    file_name: str
    file_url: str
    thumbnail_url: str | None = None
    mime_type: str | None = None
    description: str | None = None
    tags: list[str] = Field(default_factory=list)
    captured_at: str
    visibility: VisibilityType


class MediaAssetResponse(BaseModel):
    meta: ResponseMeta
    data: MediaAssetData


class MediaAssetListResponse(BaseModel):
    meta: ResponseMeta
    data: list[MediaAssetData]
