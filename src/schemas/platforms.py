from pydantic import BaseModel

class PlatformBase(BaseModel):
    platform_id: int
    platform_name: str

    class Config:
        from_attributes = True