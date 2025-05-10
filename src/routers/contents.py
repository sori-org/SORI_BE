from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.models.contents import Content
from src.models.users import User
from src.db import get_db
from src.services.image_generator import generate_marketing_image
from src.schemas.contents import ContentCreate
from src.services.auth.dependencies import get_current_user
from pydantic import BaseModel

router = APIRouter()


@router.post("/contents")
def create_content(
    data: ContentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    content = Content(**data.dict(), user_id=current_user.user_id)
    db.add(content)
    db.commit()
    db.refresh(content)

    return {
        "content_id": content.content_id,
        "message": "콘텐츠가 생성되었습니다."
    }

@router.post("/contents/{content_id}/generate-image")
def generate_image(content_id: int, db: Session = Depends(get_db)):
    """
    별도 API로 이미지 생성 실행.
    """
    content = db.query(Content).filter(Content.content_id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    # 이미지 생성 실행
    image_url = generate_marketing_image(content, db)

    return {
        "content_id": content.content_id,
        "image_url": image_url,
        "result_text": content.result_text
    }
# 📌 업데이트용 pydantic 모델
class FieldUpdate(BaseModel):
    value: int


class TextUpdate(BaseModel):
    value: str


# 📌 각 항목 업데이트 라우터
@router.post("/contents/{content_id}/platform")
def update_platform(content_id: int, update: FieldUpdate, db: Session = Depends(get_db)):
    return update_field(db, content_id, 'platform_id', update.value)


@router.post("/contents/{content_id}/item")
def update_item(content_id: int, update: FieldUpdate, db: Session = Depends(get_db)):
    return update_field(db, content_id, 'item_id', update.value)


@router.post("/contents/{content_id}/age")
def update_age(content_id: int, update: FieldUpdate, db: Session = Depends(get_db)):
    return update_field(db, content_id, 'age_id', update.value)


@router.post("/contents/{content_id}/gender")
def update_gender(content_id: int, update: FieldUpdate, db: Session = Depends(get_db)):
    return update_field(db, content_id, 'gender_id', update.value)


@router.post("/contents/{content_id}/format")
def update_format(content_id: int, update: FieldUpdate, db: Session = Depends(get_db)):
    return update_field(db, content_id, 'format_id', update.value)


@router.post("/contents/{content_id}/external")
def update_external_data(content_id: int, update: FieldUpdate, db: Session = Depends(get_db)):
    return update_field(db, content_id, 'external_data_id', update.value)


@router.post("/contents/{content_id}/prompt")
def update_user_prompt(content_id: int, update: TextUpdate, db: Session = Depends(get_db)):
    return update_field(db, content_id, 'request_text', update.value)


# 📌 공통 업데이트 처리 함수
def update_field(db, content_id, field_name, value):
    content = db.query(Content).filter(Content.content_id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    setattr(content, field_name, value)
    db.commit()
    return {"message": f"{field_name} updated successfully"}
