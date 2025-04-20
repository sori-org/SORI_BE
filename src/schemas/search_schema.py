rom pydantic import BaseModel

class PlaceSearchResponse(BaseModel):
    title: str
    category: str
    address: str
