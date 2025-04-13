from pydantic import BaseModel
from typing import List, Optional

class ContentCreateRequest(BaseModel):
    user_id: int
    platform_id: int
    item_id: int
    format_id: int
    external_data_ids: List[int]
    gender_id: Optional[int]
    age_id: Optional[int]
    request: Optional[str] = None
