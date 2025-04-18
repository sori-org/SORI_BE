from pydantic import BaseModel

class StoreCreate(BaseModel):
    user_id: int  # 추후 로그인 연동 시 자동 처리
    store_name: str
    store_address: str
    store_category: str
    store_phone: str

class StoreResponse(BaseModel):
    message: str = "가게가 성공적으로 등록되었습니다."
    store_id: int
