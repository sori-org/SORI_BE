from pydantic import BaseModel
from typing import Optional, List
from src.schemas.store_schema import StoreOut

class UserBase(BaseModel):
    display_name: str
    profile_image: Optional[str] = None


class UserCreate(UserBase):
    account_id: int  # 반드시 포함되어야 함


class UserOut(UserBase):
    userId: int = Field(..., alias="user_id")
    accountId: int = Field(..., alias="account_id")
    displayName: str = Field(..., alias="display_name")
    mainStoreId: Optional[int] = Field(None, alias="main_store_id")
    storeList: Optional[List[StoreOut]] = []

    class Config:
        from_attributes = True
        populate_by_name = True