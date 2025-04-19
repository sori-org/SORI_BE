from pydantic import BaseModel

class AgeBase(BaseModel):
    age_id: int
    age_category: str

    class Config:
        from_attributes = True