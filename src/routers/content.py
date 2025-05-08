from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.schemas.content_schema import ContentInput, ContentResult
from src.services.content_service import save_content_and_generate, get_content_result
from src.db.database import get_db
from src.services.auth.dependencies import get_current_user
from src.models.users import User

router = APIRouter(
    prefix="/api/content",
    tags=["Content Generation"]
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
