from pydantic import BaseModel

class FormatBase(BaseModel):
    format_id: int
    format_name: str

    class Config:
        orm_mode = True