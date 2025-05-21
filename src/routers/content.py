from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile, Form
from sqlalchemy.orm import Session
from src.schemas.content_schema import ContentInput, ContentResult, ContentListResponse, ContentDetailResponse
from src.services.content_service import save_content_and_generate, get_content_result
from src.db.database import get_db
from src.services.auth.dependencies import get_current_user
from src.models.users import User
from src.models.contents import Content
from src.models.stores import Store
from src.services.image_generator import generate_marketing_image
from src.schemas.contents import ContentCreate
from pydantic import BaseModel
from uuid import uuid4
from typing import Literal, Optional, List
import json
import os

router = APIRouter(
    prefix="/api/content",
    tags=["콘텐츠 생성 & 기록보기"]
)

# [0] 사용자 입력 저장 + 내부 생성
@router.post("/inputs", summary="콘텐츠 생성 (1): 사용자 선택 입력 -> 결과 생성")
def store_content_input(
    store_id: int = Form(...),
    sns_platform: str = Form(...),
    promotion_target: str = Form(...),
    promotion_name: Optional[str] = Form(""),
    gender_target: str = Form(...),
    age_range_target: str = Form(...),
    content_format: str = Form(...),
    external_sources: Optional[str] = Form(""),
    user_prompt: Optional[str] = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # external_sources가 문자열로 오면 파싱해줌
    try:
        ext_sources = json.loads(external_sources) if external_sources else []
    except Exception:
        ext_sources = []

    from src.schemas.content_schema import ContentInput  # ContentInput import 위치 맞게 수정

    # ContentInput 인스턴스 생성 (필드 맞게 전달)
    payload = ContentInput(
        store_id=store_id,
        sns_platform=sns_platform,
        promotion_target=promotion_target,
        promotion_name=promotion_name,
        gender_target=gender_target,
        age_range_target=age_range_target,
        content_format=content_format,
        external_sources=ext_sources,
        user_prompt=user_prompt,
    )

    content_id = save_content_and_generate(db, current_user.user_id, payload)
    content = db.query(Content).filter(Content.content_id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="생성된 콘텐츠 조회 실패")

    if content.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="콘텐츠 소유자 불일치")

    image_url = generate_marketing_image(content, db)

    content.image_url = image_url
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"이미지 URL 저장 실패: {str(e)}")

    return {
        "content_id": content_id,
        "image_url": image_url,
        "message": "콘텐츠(텍스트+이미지) 생성 완료"
    }

# [1] 최종 결과 조회
@router.get("/result/{content_id}", response_model=ContentResult, summary="콘텐츠 생성 (2): content_id 입력 -> 이미지, 홍보문구, 해시태그 반환")
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
@router.get("/", response_model=list[ContentListResponse], summary="콘텐츠 기록 보기(최신순/오래된순): 가게명&생성일")
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

    results = query.all()
    return [ContentListResponse.from_orm(r) for r in results]

# [3] 기록 보기: 상세
@router.get("/{content_id}", response_model=ContentDetailResponse, summary = "기록 보기 상세: content_id 입력 -> 이미지, 홍보문구, 해시태그 반환")
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

    return ContentDetailResponse.from_orm(content)




# [4] 이미지 생성
@router.post("/{content_id}/generate-image", summary="이미지 생성")
def generate_image(
    content_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    content = db.query(Content).filter(Content.content_id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    if content.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="해당 콘텐츠에 대한 권한이 없습니다.")

    #
    image_url = generate_marketing_image(content, db)

    #db commit
    content.image_url = image_url
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"이미지 URL 저장 실패: {str(e)}")

    return {"content_id": content.content_id, "image_url": image_url}

# [6] 콘텐츠 항목별 업데이트 모델
class FieldUpdate(BaseModel):
    value: int

class TextUpdate(BaseModel):
    value: str


@router.post("/{content_id}/prompt")
def update_prompt(content_id: int, update: TextUpdate, db: Session = Depends(get_db)):
    return update_field(db, content_id, 'request_text', update.value)

@router.post("/{content_id}/upload-image")
def upload_user_image(
    content_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    content = db.query(Content).filter(Content.content_id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")


    ext = os.path.splitext(file.filename)[1]
    filename = f"content_{content_id}_uploaded_image{ext}"
    file_path = os.path.join("uploaded_images", filename)

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    image_url = f"/uploaded_images/{filename}"
    content.user_image_url = image_url
    db.commit()
    return {"message": "콘텐츠 이미지 업로드 완료", "user_image_url": image_url}

# [9] 공통 업데이트 처리 함수
def update_field(db, content_id, field_name, value):
    content = db.query(Content).filter(Content.content_id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    setattr(content, field_name, value)
    db.commit()
    return {"message": f"{field_name} updated successfully"}
