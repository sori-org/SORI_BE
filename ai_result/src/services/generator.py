from sqlalchemy.orm import Session
from src.models.common import Platform, Item, Format, Gender, Age, ExternalData
from src.database.session import SessionLocal
import openai, os
from src.core.config import settings

openai.api_key = settings.OPENAI_API_KEY

PLATFORM_FILE_MAP = {
    1: "instagram.txt",
    2: "twitter.txt",
    3: "blog.txt"
}

def load_template(file_name: str) -> str:
    path = os.path.join(os.path.dirname(__file__), "..", "prompt_templates", file_name)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def resolve_names(data: dict) -> dict:
    db: Session = SessionLocal()

    item = db.query(Item).filter(Item.item_id == data["item_id"]).first()
    platform = db.query(Platform).filter(Platform.platform_id == data["platform_id"]).first()
    format = db.query(Format).filter(Format.format_id == data["format_id"]).first()
    gender = db.query(Gender).filter(Gender.gender_id == data["gender_id"]).first() if data.get("gender_id") else None
    age = db.query(Age).filter(Age.age_id == data["age_id"]).first() if data.get("age_id") else None
    external = db.query(ExternalData).filter(ExternalData.external_data_id.in_(data["external_data_ids"])).all()

    return {
        "item": item.name if item else "홍보 대상",
        "platform": platform.name if platform else "SNS",
        "format": format.name if format else "기본형",
        "gender": gender.name if gender else "전체",
        "age": age.name if age else "전체 연령대",
        "external": ", ".join(e.name for e in external),
        "request": data.get("request", "없음")
    }

def build_prompt_from_template(data: dict) -> str:
    file_name = PLATFORM_FILE_MAP.get(data["platform_id"], "default.txt")
    template = load_template(file_name)
    context = resolve_names(data)
    return template.format(**context)

async def generate_content(data: dict):
    prompt = build_prompt_from_template(data)

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )

    text = response["choices"][0]["message"]["content"]

    caption = text.split("\n")[0]
    hashtags = [h.strip() for h in text.split("해시태그:")[-1].split(",")]

    return {
        "caption": caption,
        "hashtags": hashtags,
        "image_url": "https://example.com/temp.jpg"
    }
