import os
import openai
from dotenv import load_dotenv
from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.schemas.content_schema import ContentInput
from src.models.contents import Content
from src.models.stores import Store
from src.services.external_data_service import (
    get_weather_data, get_event_data, get_review_data
)
import re



# .env 불러오기
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# 프롬프트 경로
PROMPT_DIR = "src/prompts"
SNS_PROMPT_MAP = {
    "instagram": "instagram.txt",
    "naver_cafe": "naver_cafe.txt",
    "twitter": "X.txt"
}

# 매핑 테이블
PLATFORM_MAP = {"instagram": 1, "twitter": 2, "naver_cafe": 3}
FORMAT_MAP = {"image_text": 1, "cuttoon": 2, "cover_text": 3}
GENDER_MAP = {"male": 1, "female": 2}
AGE_MAP = {"10-20": 1, "20-30": 2, "30-40": 3, "40-50": 4}
EXTERNAL_DATA_MAP = {"weather": 1, "review": 2, "event": 3, "trend": 4}

# SNS별 프롬프트 불러오기
def load_prompt_for_sns(sns_platform: str) -> str:
    filename = SNS_PROMPT_MAP.get(sns_platform)
    if not filename:
        raise HTTPException(status_code=400, detail="지원되지 않는 SNS 플랫폼입니다.")
    filepath = os.path.join(PROMPT_DIR, filename)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="프롬프트 파일을 찾을 수 없습니다.")

# GPT 문구 생성 함수
def gpt_generate_text(prompt: str) -> str:
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except (IndexError, AttributeError):
        raise HTTPException(status_code=500, detail="GPT 응답 파싱 실패")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GPT 호출 실패: {str(e)}")


# GPT 응답에서 문구와 해시태그 분리
def split_gpt_response(response: str) -> tuple[str, str]:
    hashtags = re.findall(r"#\S+", response)
    text_without_hashtags = re.sub(r"#\S+", "", response).strip()
    return text_without_hashtags.strip(), " ".join(hashtags)


# 콘텐츠 생성 및 DB 저장
def save_content_and_generate(db: Session, user_id: int, data: ContentInput) -> int:
    # 외부 데이터 수집
    extra_info = []
    if "weather" in data.external_sources:
        extra_info.append(get_weather_data("Seoul"))
    if "event" in data.external_sources:
        extra_info.append(get_event_data("1"))
    if "review" in data.external_sources:
        extra_info.append(get_review_data(data.promotion_name))
    external_context = "\n".join(extra_info)

    # store_id 유효성 검사
    store = db.query(Store).filter(Store.store_id == data.store_id).first()
    if not store:
        raise HTTPException(status_code=400, detail="유효하지 않은 store_id입니다.")

    # 외부 데이터 매핑 키 검사
    external_data_id = None
    if data.external_sources:
        key = data.external_sources[0]
        if key not in EXTERNAL_DATA_MAP:
            raise HTTPException(status_code=400, detail=f"지원되지 않는 외부 데이터 타입입니다: {key}")
        external_data_id = EXTERNAL_DATA_MAP[key]

    try:
        content = Content(
            user_id=user_id,
            store_id=data.store_id,
            platform_id=PLATFORM_MAP.get(data.sns_platform),
            format_id=FORMAT_MAP.get(data.content_format),
            item_id=None,
            age_id=AGE_MAP.get(data.age_range_target),
            gender_id=GENDER_MAP.get(data.gender_target),
            external_data_id=external_data_id,
            request_text=data.promotion_name
        )
        db.add(content)
        db.commit()
        db.refresh(content)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"DB 저장 실패: {str(e)}")

    # GPT 전체 응답 → 문구 + 해시태그 추출
    base_prompt = load_prompt_for_sns(data.sns_platform)
    full_prompt = f"""{base_prompt}

<추가 정보>
- 홍보 대상: {data.promotion_name}
- 타겟층: {data.gender_target}, {data.age_range_target}
- 콘텐츠 형식: {data.content_format}
- 외부 정보:
{external_context}
"""
    full_response = gpt_generate_text(full_prompt)
    result_text, result_hashtag = split_gpt_response(full_response)

    content.result_text = result_text
    content.result_hashtag = result_hashtag

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"최종 DB 커밋 실패: {str(e)}")

    return content.content_id

# 콘텐츠 생성 결과 조회
def get_content_result(db: Session, content_id: int):
    content = db.query(Content).filter(Content.content_id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="해당 콘텐츠를 찾을 수 없습니다.")
    return content
