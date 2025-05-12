from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ContentBase(BaseModel):
    content_id: int
    user_id: int
    platform_id: int
    format_id: int | None
    item_id: int | None
    external_data_id: int
    image_url: str
    request_text: str

    class Config:
        from_attributes = True

from pydantic import BaseModel
from typing import Optional

class ContentCreate(BaseModel):
    user_id: int
    platform_id: int
    format_id: Optional[int]
    item_id: Optional[int]
    age_id: Optional[int]
    gender_id: Optional[int]
    external_data_id: Optional[int]
    request_text: Optional[str]