from fastapi import APIRouter, Query
from src.services.naver_search import search_places
from src.schemas.search_schema import PlaceSearchResponse

router = APIRouter(tags=["search"])

@router.get("/place", response_model=list[PlaceSearchResponse])
def search_store(search_keyword: str = Query(..., description="검색할 키워드")):
    return search_places(search_keyword)
