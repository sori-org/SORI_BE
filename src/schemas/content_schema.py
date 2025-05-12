from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# 사용자 입력 데이터 스키마
class ContentInput(BaseModel):
    store_id: int
    sns_platform: str = Field(..., example="instagram")
    promotion_target: str = Field(..., example="store")  # store or menu
    promotion_name: str = Field(..., example="우리동네 베이커리")
    gender_target: str = Field(..., example="female")  # female or male
    age_range_target: str = Field(..., example="20-30")
    content_format: str = Field(..., example="image_text")  # image_text, cuttoon, cover_text
    external_sources: Optional[List[str]] = Field(default=[], example=["weather", "review"])

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
    text: str
    hashtags: List[str]
    image_url: Optional[str] = None


class ContentCreationResponse(BaseModel):
    content_id: int
    message: str


class ContentListResponse(BaseModel):
    content_id: int
    created_at: datetime
    store_name: Optional[str] = None  # ← store 테이블과 조인 필요

    class Config:
        from_attributes = True  # pydantic v2



class ContentDetailResponse(BaseModel):
    content_id: int
    platform_id: Optional[int]
    result_text: str
    result_hashtag: str
    image_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
