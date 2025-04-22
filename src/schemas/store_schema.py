from pydantic import BaseModel
from typing import Optional

class StoreCreate(BaseModel):
    user_id: int  # 추후 로그인 연동 시 자동 처리
    store_name: str
    store_address: str
    store_category: str
    store_phone: str
    store_description: str

class StoreResponse(BaseModel):
    message: str = "가게가 성공적으로 등록되었습니다."
    store_id: int

class StoreOut(BaseModel):
    store_id: int
    store_name: str
    store_address: Optional[str]
    store_category: Optional[str]
    store_phone: Optional[str]
    store_description: Optional[str]

    class Config:
        from_attributes = True
        populate_by_name = True


class StoreUpdate(BaseModel):
    name: str
    phone: str
    description: str
