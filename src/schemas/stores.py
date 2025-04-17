from pydantic import BaseModel, Field

class StoreBase(BaseModel):
    id: int = Field(..., alias="store_id")
    name: str = Field(..., alias="store_name")
    address: str = Field(..., alias="store_address")
    category: str = Field(..., alias="store_category")
    phone: str = Field(..., alias="store_phone")
    description: str = Field(..., alias="store_description")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True