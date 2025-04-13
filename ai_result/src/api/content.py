from fastapi import APIRouter, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session
from src.database.session import get_db
from src.models.content import Content
from src.services.generator import generate_content
import json

router = APIRouter()

@router.post("/generate")
async def create_content(
    data: str = Form(...),
    image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    parsed = json.loads(data)
    result = await generate_content(parsed)

    new_content = Content(
        user_id=parsed["user_id"],
        platform_id=parsed["platform_id"],
        item_id=parsed["item_id"],
        format_id=parsed["format_id"],
        external_data_id=parsed["external_data_ids"][0],  # 단일 저장
        gender_id=parsed.get("gender_id"),
        age_id=parsed.get("age_id"),
        request=parsed.get("request"),
        result_image=result["image_url"],
        text_and_hashtag=result["caption"] + "\n" + ", ".join(result["hashtags"])
    )
    db.add(new_content)
    db.commit()
    db.refresh(new_content)

    return {
        "content_id": new_content.content_id,
        **result
    }
