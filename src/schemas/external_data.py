from pydantic import BaseModel

class ExternalDataBase(BaseModel):
    external_data_id: int
    external_data_name: str
    class Config:
        from_attributes = True
