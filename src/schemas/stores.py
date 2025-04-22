from pydantic import BaseModel, Field
from typing import Optional

class StoreBase(BaseModel):
    id: int = Field(..., alias="store_id")
    store_name: str = Field(..., alias="name")
    store_address: str = Field(..., alias="address")
    store_category: str = Field(..., alias="category")
    store_phone: str = Field(..., alias="phone")
    store_description: str = Field(..., alias="description")

    class Config:
        from_attributes = True
        populate_by_name = True

class StoreOut(BaseModel):
    store_id: int
    store_name: str
    store_address: Optional[str]
    store_category: Optional[str]
    store_phone: Optional[str]
    store_description: Optional[str]

    class Config:
        from_attributes = True