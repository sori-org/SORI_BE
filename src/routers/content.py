from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from src.schemas.content_schema import ContentInput, ContentResult, ContentListResponse, ContentDetailResponse
from src.services.content_service import save_content_and_generate, get_content_result
from src.db.database import get_db
from src.services.auth.dependencies import get_current_user
from src.models.users import User
from src.models.contents import Content
from src.models.stores import Store
from typing import Literal

router = APIRouter(
    prefix="/api/content",
    tags=["Content Generation & Records"]
)

# [0] 사용자 입력 저장 + 내부 생성
@router.post("/inputs", summary="사용자 입력 저장 및 콘텐츠 생성 API")
def store_content_input(
    payload: ContentInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    content_id = save_content_and_generate(db, current_user.user_id, payload)
    return {
        "content_id": content_id,
        "message": "콘텐츠 생성 완료. content_id를 사용해서 생성된 콘텐츠 조회하기!"
    }


# [1] 최종 결과 조회
@router.get("/result/{content_id}", response_model=ContentResult, summary="최종 결과 조회 API")
def get_final_content(content_id: int, db: Session = Depends(get_db)):
    content = get_content_result(db, content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    return ContentResult(
        content_id=content.content_id,
        text=content.result_text,
        hashtags=content.result_hashtag.split() if content.result_hashtag else [],
        image_url=content.image_url
    )


# [2] 콘텐츠 기록 보기
@router.get("/", response_model=list[ContentListResponse], summary="콘텐츠 기록 보기: 가게명&생성일")
def get_content_list(
    sort_by: Literal["latest", "oldest"] = Query("latest"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(
        Content.content_id,
        Content.created_at,
        Store.store_name
    ).join(Store, Content.store_id == Store.store_id) \
     .filter(Content.user_id == current_user.user_id)

    if sort_by == "latest":
        query = query.order_by(Content.created_at.desc())
    else:
        query = query.order_by(Content.created_at.asc())

    return query.all()


# [3] 기록 보기: 상세
@router.get("/{content_id}", response_model=ContentDetailResponse, summary = "기록 보기: 상세")
def get_content_detail(
    content_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    content = db.query(Content).filter(
        Content.content_id == content_id,
        Content.user_id == current_user.user_id
    ).first()

    if not content:
        raise HTTPException(status_code=404, detail="콘텐츠를 찾을 수 없습니다.")

    return content


