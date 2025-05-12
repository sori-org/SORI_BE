from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.models.contents import Content
from src.db import get_db
from src.services.image_generator import generate_marketing_image
from src.schemas.contents import ContentCreate

router = APIRouter()

@router.post("/test-image-generation/{content_id}")
def test_image_generation(content_id: int, db: Session = Depends(get_db)):
    content = db.query(Content).filter(Content.content_id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    image_url = generate_marketing_image(content, db)
    return {"image_url": image_url}

@router.post("/contents")
def create_content(data: ContentCreate, db: Session = Depends(get_db)):
    content = Content(**data.dict())
    db.add(content)
    db.commit()
    db.refresh(content)

    # 바로 이미지 생성도 실행
    generate_marketing_image(content, db)

    return {
        "content_id": content.content_id,
        "image_url": content.image_url,
        "result_text": content.result_text
    }