from fastapi import APIRouter, Query
from src.services.naver_search import search_places
from src.schemas.search_schema import PlaceSearchResponse


router = APIRouter(
    prefix="/api/search",
    tags=["가게 검색"]
)
@router.get("/place", response_model=list[PlaceSearchResponse], summary="가게 검색: 가게명 입력 -> 검색 결과 4개 출력")
def search_store(search_keyword: str = Query(..., description="검색할 키워드")):
    return search_places(search_keyword)
