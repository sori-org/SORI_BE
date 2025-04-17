from pydantic import BaseModel

class AgeBase(BaseModel):
    age_id: int
    age_category: str

    class Config:
        orm_mode = True