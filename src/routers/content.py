from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile
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
from typing import Literal
import os

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

# [4] 기본 콘텐츠 생성
@router.post("", summary="기본 콘텐츠 생성")
def create_content(
    data: ContentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    content = Content(**data.dict(), user_id=current_user.user_id)
    db.add(content)
    db.commit()
    db.refresh(content)
    return {"content_id": content.content_id, "message": "콘텐츠가 생성되었습니다."}

# [5] 이미지 생성
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
    image_url = generate_marketing_image(content, db)
    return {"content_id": content.content_id, "image_url": image_url}

# [6] 콘텐츠 항목별 업데이트 모델
class FieldUpdate(BaseModel):
    value: int

class TextUpdate(BaseModel):
    value: str

# [7] 항목 업데이트 라우트
@router.post("/{content_id}/platform")
def update_platform(content_id: int, update: FieldUpdate, db: Session = Depends(get_db)):
    return update_field(db, content_id, 'platform_id', update.value)

@router.post("/{content_id}/item")
def update_item(content_id: int, update: FieldUpdate, db: Session = Depends(get_db)):
    return update_field(db, content_id, 'item_id', update.value)

@router.post("/{content_id}/age")
def update_age(content_id: int, update: FieldUpdate, db: Session = Depends(get_db)):
    return update_field(db, content_id, 'age_id', update.value)

@router.post("/{content_id}/gender")
def update_gender(content_id: int, update: FieldUpdate, db: Session = Depends(get_db)):
    return update_field(db, content_id, 'gender_id', update.value)

@router.post("/{content_id}/format")
def update_format(content_id: int, update: FieldUpdate, db: Session = Depends(get_db)):
    return update_field(db, content_id, 'format_id', update.value)

@router.post("/{content_id}/external")
def update_external(content_id: int, update: FieldUpdate, db: Session = Depends(get_db)):
    return update_field(db, content_id, 'external_data_id', update.value)

@router.post("/{content_id}/prompt")
def update_prompt(content_id: int, update: TextUpdate, db: Session = Depends(get_db)):
    return update_field(db, content_id, 'request_text', update.value)

# [8] 이미지 업로드
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
    content_dir = os.path.join("uploaded_images", f"content_{content_id}")
    os.makedirs(content_dir, exist_ok=True)
    ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid4().hex}{ext}"
    file_path = os.path.join(content_dir, unique_filename)
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    image_url = f"/static/content_{content_id}/{unique_filename}"
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
