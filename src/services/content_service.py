import os
import openai
from dotenv import load_dotenv
from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.schemas.content_schema import ContentInput
from src.models.contents import Content
from src.models.stores import Store
from src.models.items import Item
from src.models.external_data import ExternalData
from src.services.external_data_service import (
    get_weather_data, get_event_data, get_review_data
)
from src.services.external_api import get_external_data_multi
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
FORMAT_MAP = {"image+text": 1, "cut_toon": 2, "post_cover+text": 3}
GENDER_MAP = {"male": 1, "female": 2}
AGE_MAP = {"10-20": 1, "20-30": 2, "30-40": 3, "40+": 4}
EXTERNAL_DATA_MAP = {"weather": 1, "review": 2, "festival": 3, "trend": 4}

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

# promotion_target에서 item_id를 추출
def resolve_id_by_name(db: Session, model, name_field: str, name_value: str, id_field: str = "id") -> int | None:
    if not name_value:
        return None
    row = db.query(model).filter(getattr(model, name_field) == name_value).first()
    return getattr(row, id_field) if row else None

# GPT 문구 생성 함수
def gpt_generate_text(prompt: str, platform: str = "") -> str:
    try:
        response = openai.chat.completions.create(
            model="gpt-4.1",
            messages=[{"role": "user", "content": prompt}]
        )
        result_text = response.choices[0].message.content.strip()

        if platform == "instagram":
            result_text = result_text[:1000]

        return result_text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GPT 호출 실패: {str(e)}")




# GPT 응답에서 문구와 해시태그 분리
def split_gpt_response(response: str, platform: str) -> tuple[str, str]:
    try:
        if platform == "naver_cafe":
            title_match = re.search(r"\[제목\](.*?)\[본문\]", response, re.DOTALL)
            body_match = re.search(r"\[본문\](.*?)\[해시태그\]", response, re.DOTALL)
            tags_match = re.search(r"\[해시태그\](.*)", response, re.DOTALL)

            if not (title_match and body_match and tags_match):
                raise ValueError("네이버 카페 응답 구조가 맞지 않습니다.")

            title = title_match.group(1).strip()
            body = body_match.group(1).strip()
            raw_tags = tags_match.group(1)

            hashtags = re.findall(r"#([A-Za-z0-9가-힣_]+)", raw_tags)
            hashtag_line = " ".join(f"#{tag}" for tag in hashtags)

            clean_text = f"{title}\n\n{body}"
            return clean_text, hashtag_line

        else:
            text_match = re.search(r"\[문구\](.*?)\[해시태그\]", response, re.DOTALL)
            tags_match = re.search(r"\[해시태그\](.*)", response, re.DOTALL)

            if not (text_match and tags_match):
                raise ValueError("응답 구조가 맞지 않습니다.")

            clean_text = text_match.group(1).strip()
            raw_tags = tags_match.group(1)

            hashtags = re.findall(r"#([A-Za-z0-9가-힣_]+)", raw_tags)
            hashtag_line = " ".join(f"#{tag}" for tag in hashtags)

            return clean_text, hashtag_line
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GPT 응답 파싱 실패: {str(e)}")


# 콘텐츠 생성 및 DB 저장
def save_content_and_generate(db: Session, user_id: int, data: ContentInput) -> int:
    # 외부 데이터 수집
    store = db.query(Store).filter(Store.store_id == data.store_id).first()
    if not store:
        raise HTTPException(status_code=400, detail="유효하지 않은 store_id입니다.")

    external_context = get_external_data_multi(data.external_sources, store.store_address, data.promotion_name)
    # store_id 유효성 검사
    store = db.query(Store).filter(Store.store_id == data.store_id).first()
    if not store:
        raise HTTPException(status_code=400, detail="유효하지 않은 store_id입니다.")

    # 외부 데이터 저장 (M2M 관계로)
    external_data_objs = []
    if data.external_sources:
        for key in data.external_sources:
            key = key.strip()
            external_data_id = EXTERNAL_DATA_MAP.get(key)
            if external_data_id:
                ext = db.query(ExternalData).filter(ExternalData.external_data_id == external_data_id).first()
                if ext:
                    external_data_objs.append(ext)

    target = data.promotion_target
    if target == "menu":
        target = "product"
    item_id = resolve_id_by_name(db, Item, "item_name", target, "item_id")

    try:
        content = Content(
            user_id=user_id,
            store_id=data.store_id,
            platform_id=PLATFORM_MAP.get(data.sns_platform),
            format_id=FORMAT_MAP.get(data.content_format),
            item_id=item_id,
            age_id=AGE_MAP.get(data.age_range_target),
            gender_id=GENDER_MAP.get(data.gender_target),
            external_data_list=external_data_objs,
            request_text=data.user_prompt,
        )
        db.add(content)
        db.commit()
        db.refresh(content)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"DB 저장 실패: {str(e)}")

    # GPT 전체 응답 → 문구 + 해시태그 추출
    base_prompt = load_prompt_for_sns(data.sns_platform)

    store_info = (
    f"가게 이름: {store.store_name}\n"
    f"주소: {store.store_address}\n"
    f"전화번호: {store.store_phone}"
    )


    full_prompt = (
    f"{base_prompt}\n\n"
    f"<추가 정보>\n"
    f"- 홍보 대상: {data.promotion_name}\n"
    f"- 타겟층: {data.gender_target}, {data.age_range_target}\n"
    f"- 콘텐츠 형식: {data.content_format}\n"
    f"- 외부 정보:\n{external_context}\n"
    f"- 추가 설명:\n{data.user_prompt}\n"
    f"<가게 정보>\n{store_info}"
    )
    full_response = gpt_generate_text(full_prompt, platform=data.sns_platform)
    result_text, result_hashtag = split_gpt_response(full_response, platform=data.sns_platform)

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
