from pydantic import BaseModel

class GenderBase(BaseModel):
    gender_id: int
    gender_category: str

    class Config:
        orm_mode = True