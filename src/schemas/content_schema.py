from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime

# 사용자 입력 데이터 스키마
class ContentInput(BaseModel):
    store_id: int
    sns_platform: str = Field(..., example="instagram")
    promotion_target: str = Field(..., example="store")  # store or menu
    promotion_name: Optional[str] = Field(..., example="우리동네 베이커리")
    gender_target: str = Field(..., example="female")  # female or male
    age_range_target: str = Field(..., example="20-30")
    content_format: str = Field(..., example="image+text")  # image+text, cut_toon, post_cover+text
    external_sources: Optional[List[str]] = Field(default=[], example=["weather", "review"])
    user_prompt: Optional[str] = Field(default="", example="맛있는 소보로빵이 유명합니다.")
# 이미지 업로드 후 응답
class ContentImageUpload(BaseModel):
    image_url: str


# 문구 생성 결과
class ContentTextResponse(BaseModel):
    text: str


# 해시태그 생성 결과
class ContentHashtagResponse(BaseModel):
    hashtags: List[str]


# 이미지 생성 결과
class ContentImageResponse(BaseModel):
    image_url: str


# 최종 결과 조회
class ContentResult(BaseModel):
    content_id: int
    text: Optional[str]
    hashtags: Optional[List[str]]
    image_url: Optional[str] = None


class ContentCreationResponse(BaseModel):
    content_id: int
    message: str


class ContentListResponse(BaseModel):
    content_id: int
    created_at: datetime
    store_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_orm(cls, obj):
        return cls(
            content_id=obj.content_id,
            created_at=obj.created_at,
            store_name=getattr(obj, "store_name", None)
        )


class ContentDetailResponse(BaseModel):
    content_id: int
    platform_id: Optional[int]
    result_text: Optional[str]
    result_hashtag: Optional[str]
    image_url: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_orm(cls, obj):
        return cls(
            content_id=obj.content_id,
            platform_id=obj.platform_id,
            result_text=obj.result_text,
            result_hashtag=obj.result_hashtag,
            image_url=obj.image_url,
            created_at=obj.created_at
        )
