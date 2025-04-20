from pydantic import BaseModel, Field

class StoreBase(BaseModel):
    id: int = Field(..., alias="store_id")
    name: str = Field(..., alias="store_name")
    address: str = Field(..., alias="store_address")
    category: str = Field(..., alias="store_category")
    phone: str = Field(..., alias="store_phone")
    description: str = Field(..., alias="store_description")

    class Config:
        from_attributes = True
        allow_population_by_field_name = True


class StoreUpdate(BaseModel):
    name: str
    phone: str
    description: str

class StoreOut(BaseModel):
    store_id: int
    name: str
    phone: str
    description: str

    class Config:
        orm_mode = True


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

class StoreUpdate(BaseModel):
    name: str
    phone: str
    description: str

class StoreOut(BaseModel):
    store_id: int
    name: str
    phone: str
    description: str

    class Config:
        orm_mode = True
