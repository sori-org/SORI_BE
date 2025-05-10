from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from src.models.contents import Content
from src.models.platforms import Platform
from src.models.formats import Format
from src.models.items import Item
from src.models.ages import Age
from src.models.genders import Gender
from src.models.external_data import ExternalData
from src.models.users import User
from src.models.stores import Store
from sqlalchemy.orm import Session
import requests
import os

api_key = os.getenv("OPENAI_API_KEY")
MAX_PROMPT_LENGTH = 4000

def download_image(image_url, filename):
    response = requests.get(image_url)
    if response.status_code == 200:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"이미지 저장 완료: {filename}")
    else:
        print(f"이미지 다운로드 실패: {response.status_code}")

def get_store_info(db, user_id):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user or not user.main_store_id:
        return None, None
    store = db.query(Store).filter(Store.store_id == user.main_store_id).first()
    if not store:
        return None, None
    return store.store_name, store.store_address

def get_text_by_id(db: Session, model, id_field, id_value, text_field="name") -> str:
    if id_value is None:
        return ""
    row = db.query(model).filter(id_field == id_value).first()
    return getattr(row, text_field) if row else ""

# ---- LangChain 통합 Assistant ----
def build_chain() -> LLMChain:
    template = """
다음 조건을 반영하여 마케팅 콘텐츠용 DALL·E 이미지 프롬프트를 작성해줘.

플랫폼: {platform}
아이템: {item}
포맷: {format}
연령대: {age}
성별: {gender}
외부 데이터: {external}
유저 요청: {user_request}

위 항목들을 모두 고려하여,
1️⃣ 플랫폼 최적화 설명
2️⃣ 상품 특징 강조
3️⃣ 연령대 및 성별에 맞는 스타일
4️⃣ 외부 데이터 연결 (예: 날씨, 리뷰, 행사, 트렌드)
5️⃣ 유저 요청 반영

이 항목들을 조화롭게 반영한 **DALL·E용 프롬프트**를 만들어줘.
"""
    prompt = PromptTemplate(
        input_variables=["platform", "item", "format", "age", "gender", "external", "user_request"],
        template=template
    )
    llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
    return LLMChain(llm=llm, prompt=prompt)

# ---- 이미지 생성 함수 ----
def generate_marketing_image(content: Content, db: Session) -> str:
    store_name, store_address = get_store_info(db, content.user_id)
    if not store_name or not store_address:
        raise Exception("대표 가게 정보가 없습니다.")

    platform_name = get_text_by_id(db, Platform, Platform.platform_id, content.platform_id, "platform_name")
    item_name = get_text_by_id(db, Item, Item.item_id, content.item_id, "item_name")
    format_name = get_text_by_id(db, Format, Format.format_id, content.format_id, "format_name")
    age_name = get_text_by_id(db, Age, Age.age_id, content.age_id, "age_category")
    gender_name = get_text_by_id(db, Gender, Gender.gender_id, content.gender_id, "gender_category")
    external_data_name = get_text_by_id(db, ExternalData, ExternalData.external_data_id, content.external_data_id, "external_data_name")

    print("platform_name:", platform_name)
    print("item_name:", item_name)
    print("format_name:", format_name)
    print("age_name:", age_name)
    print("gender_name:", gender_name)
    print("external_data_name:", external_data_name)
    print("user_request_text:", content.request_text)

    unified_chain = build_chain()
    final_prompt = unified_chain.run({
        "platform": platform_name,
        "item": item_name,
        "format": format_name,
        "age": age_name,
        "gender": gender_name,
        "external": external_data_name,
        "user_request": content.request_text
    })

    if len(final_prompt) > MAX_PROMPT_LENGTH:
        final_prompt = final_prompt[:MAX_PROMPT_LENGTH]

    print("\n===== 최종 DALL·E 프롬프트 =====\n")
    print(final_prompt)
    print("\n===== 프롬프트 끝 =====\n")

    dalle_res = requests.post(
        "https://api.openai.com/v1/images/generations",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": "dall-e-3",
            "prompt": final_prompt,
            "n": 1,
            "size": "1024x1024"
        }
    )

    if dalle_res.status_code != 200:
        raise Exception(f"DALL·E API 호출 실패: {dalle_res.status_code}, {dalle_res.text}")

    response_json = dalle_res.json()
    if "data" not in response_json or not response_json["data"]:
        raise Exception(f"DALL·E API 응답에 이미지 데이터 없음: {response_json}")

    image_url = response_json["data"][0]["url"]
    filename = f"generated_images/content_{content.content_id}.png"
    download_image(image_url, filename)

    content.image_url = image_url
    db.commit()

    return image_url
