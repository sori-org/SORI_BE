from pydantic import BaseModel, Field
from typing import List, Optional

# 사용자 입력 데이터 스키마
class ContentInput(BaseModel):
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
    content_id: str
    text: str
    hashtags: List[str]
    image_url: str
