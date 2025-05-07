import uuid
from typing import List
from src.schemas.content_schema import ContentInput
from src.models.contents import Content
from sqlalchemy.orm import Session
from fastapi import HTTPException
import os
import openai
from dotenv import load_dotenv

# .env 불러오기
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# 매핑 테이블
PLATFORM_MAP = {"instagram": 1, "facebook": 2, "naver_blog": 3}
FORMAT_MAP = {"image_text": 1, "cuttoon": 2, "cover_text": 3}
GENDER_MAP = {"male": 1, "female": 2}
AGE_MAP = {"10-20": 1, "20-30": 2, "30-40": 3, "40-50": 4}
EXTERNAL_DATA_MAP = {"weather": 1, "review": 2, "event": 3, "trend": 4}


# GPT 문구 생성 함수
def gpt_generate_text(prompt: str) -> str:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except openai.error.OpenAIError as e:
        raise HTTPException(status_code=500, detail=f"GPT 호출 실패: {str(e)}")


# 사용자 입력 저장 + GPT 문구/해시태그 생성
def save_content_and_generate(db: Session, user_id: int, data: ContentInput) -> int:
    from src.services.external_data_service import (
        get_weather_data, get_event_data, get_review_data
    )

    # 외부 정보 프롬프트용 문자열 구성
    extra_info = []
    if "weather" in data.external_sources:
        extra_info.append(get_weather_data("Seoul"))
    if "event" in data.external_sources:
        extra_info.append(get_event_data("1"))
    if "review" in data.external_sources:
        extra_info.append(get_review_data(data.promotion_name))

    external_context = "\n".join(extra_info)

    try:
        content = Content(
            user_id=user_id,
            platform_id=PLATFORM_MAP.get(data.sns_platform),
            format_id=FORMAT_MAP.get(data.content_format),
            item_id=None,
            age_id=AGE_MAP.get(data.age_range_target),
            gender_id=GENDER_MAP.get(data.gender_target),
            external_data_id=EXTERNAL_DATA_MAP.get(data.external_sources[0]) if data.external_sources else None,
            request_text=data.promotion_name
        )
        db.add(content)
        db.commit()
        db.refresh(content)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"DB 저장 실패: {str(e)}")

    # 홍보 문구 생성
    content.result_text = gpt_generate_text(
        f"""
        다음 정보를 바탕으로 짧은 홍보 문구를 만들어줘:

        - 홍보 대상: {data.promotion_name}
        - 타겟층: {data.gender_target}, {data.age_range_target}
        - 콘텐츠 형식: {data.content_format}
        - 외부 정보:
        {external_context}
        """
    )

    # 해시태그 생성
    hashtags_text = gpt_generate_text(
        f"""
        {data.promotion_name}를(을) 홍보하기 위한 해시태그를 5개 추천해줘.
        해시태그 기호 포함하고, 한글로 작성해줘.
        """
    )
    hashtags = hashtags_text.replace("\n", " ").split()
    hashtags = [tag for tag in hashtags if tag.startswith("#")]
    content.result_hashtag = " ".join(hashtags)

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"최종 DB 커밋 실패: {str(e)}")

    return content.content_id


# 최종 결과 조회
def get_content_result(db: Session, content_id: int):
    return db.query(Content).filter(Content.content_id == content_id).first()
