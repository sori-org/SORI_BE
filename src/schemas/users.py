from pydantic import BaseModel
from typing import Optional, List
from src.schemas.store_schema import StoreOut

class UserBase(BaseModel):
    display_name: str
    profile_image: Optional[str] = None


class UserCreate(UserBase):
    account_id: int  # 반드시 포함되어야 함


class UserOut(UserBase):
    user_id: int
    account_id: int
    main_store_id: Optional[int] = None
    storeList: Optional[List[StoreOut]] = []

    class Config:
        from_attributes = True
