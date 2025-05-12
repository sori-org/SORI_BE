from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from src.models.contents import Content
from src.models.platforms import Platform
from src.models.formats import Format
from src.models.items import Item
from src.models.ages import Age
from src.models.genders import Gender
from src.models.external_data import ExternalData
from sqlalchemy.orm import Session
import requests
import os

api_key = os.getenv("OPENAI_API_KEY")

# ---- Helper: 텍스트 조회 ----
def get_text_by_id(db: Session, model, id_field, id_value, text_field="name") -> str:
    if id_value is None:
        return ""
    row = db.query(model).filter(id_field == id_value).first()
    return getattr(row, text_field) if row else ""

# ---- LangChain Assistant 정의 ----
def build_chain(template: str) -> LLMChain:
    prompt = PromptTemplate(input_variables=["input"], template=template)
    llm = OpenAI(model="gpt-4o", temperature=0.7)
    return LLMChain(llm=llm, prompt=prompt)

# 각 요소별 템플릿
platform_template = """플랫폼 {input}에서 가장 효과적인 마케팅 이미지 스타일은 무엇인가요? 색상, 분위기, 레이아웃 측면에서 설명해줘."""
item_template = """상품 '{input}'을(를) 가장 잘 표현할 수 있는 이미지 스타일을 설명해줘."""
age_gender_template = """{input}를 타겟으로 하는 마케팅 이미지 스타일을 제안해줘. 배경, 인물, 표정 등을 포함해서."""
external_template = """외부 데이터 내용: {input}. 이를 시각적으로 표현하려면 어떤 이미지 요소가 좋을까?"""
user_prompt_template = """유저 요청: {input}. 이를 바탕으로 시각적 이미지 아이디어를 구체화해줘."""

# 체인 구성
platform_chain = build_chain(platform_template)
item_chain = build_chain(item_template)
age_gender_chain = build_chain(age_gender_template)
external_chain = build_chain(external_template)
user_prompt_chain = build_chain(user_prompt_template)

# ---- 이미지 생성 함수 ----
def generate_marketing_image(content: Content, db: Session) -> str:
    # ID → 텍스트 변환
    platform_name = get_text_by_id(db, Platform, Platform.platform_id, content.platform_id, text_field="platform_name")
    item_name = get_text_by_id(db, Item, Item.item_id, content.item_id, text_field="item_name")
    format_name = get_text_by_id(db, Format, Format.format_id, content.format_id, text_field="format_name")
    age_name = get_text_by_id(db, Age, Age.age_id, content.age_id, text_field="age_category")
    gender_name = get_text_by_id(db, Gender, Gender.gender_id, content.gender_id, text_field="gender_category")
    external_data_name = get_text_by_id(db, ExternalData, ExternalData.external_data_id, content.external_data_id,
                                        text_field="external_data_name")
    # 각 어시스턴트에게 개별 설명 받아오기
    fragments = {
        "platform_desc": platform_chain.run(platform_name),
        "item_desc": item_chain.run(item_name),
        "format_desc": item_chain.run(format_name),
        "age_desc": age_gender_chain.run(age_name),
        "gender_desc": age_gender_chain.run(gender_name),
        "external_desc": external_chain.run(external_data_name),
        "user_prompt_desc": user_prompt_chain.run(content.request_text)
    }

    # 프롬프트 통합
    final_prompt = f"""
아래 요소들을 반영한 마케팅 콘텐츠 이미지를 묘사해줘:

1. 플랫폼 최적화 설명: {fragments['platform_desc']}
2. 상품 특징: {fragments['item_desc']}
3. 타겟 설명 (연령/성별): {fragments['age_gender_desc']}
4. 외부 데이터 강조점: {fragments['external_desc']}
5. 유저 요청사항 해석: {fragments['user_prompt_desc']}

이 요소를 모두 반영해 DALL·E 스타일의 텍스트 프롬프트를 완성해줘.
"""

    # 이미지 생성 (OpenAI API 호출)
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
    image_url = dalle_res.json()["data"][0]["url"]

    # DB 업데이트 (선택적)
    content.image_url = image_url
    content.result_text = final_prompt
    db.commit()

    return image_url
