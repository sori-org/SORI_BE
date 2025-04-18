from pydantic import BaseModel

class ItemBase(BaseModel):
    item_id: int
    item_name: str

    class Config:
        orm_mode = True