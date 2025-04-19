from pydantic import BaseModel

class ContentBase(BaseModel):
    content_id: int
    user_id: int
    platform_id: int
    format_id: int | None
    item_id: int | None
    external_data_id: int
    image_url: str
    request_text: str

    class Config:
        from_attributes = True