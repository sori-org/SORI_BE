from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
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
from src.services.external_api import get_external_data_multi
import base64
import requests
import os

api_key = os.getenv("OPENAI_API_KEY")
MAX_PROMPT_LENGTH = 4000

# 파일 읽기 함수
def load_system_message(filepath: str) -> str:
    with open(filepath, "r", encoding="utf-8") as file:
        return file.read()
# main_store_id를 이용해 store 정보 취득
def get_store_info(db, user_id):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user or not user.main_store_id:
        return None, None, None
    store = db.query(Store).filter(Store.store_id == user.main_store_id).first()
    if not store:
        return None, None, None
    return store.store_name, store.store_address, store.store_description

# 콘텐츠의 외래키 id로 각 카테고리의 이름 취득
def get_text_by_id(db: Session, model, id_field, id_value, text_field="name") -> str:
    if id_value is None:
        return ""
    row = db.query(model).filter(id_field == id_value).first()
    return getattr(row, text_field) if row else ""

# 업로드한 이미지를 글로 분석
def describe_user_image(content: Content) -> str:
    if not content.user_image_url:
        return ""

    image_path = content.user_image_url
    if image_path.startswith("/uploaded_images/"):
        image_path = image_path.replace("/uploaded_images/", "uploaded_images/")

    if not os.path.exists(image_path):
        return ""

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    encoded_image = base64.b64encode(image_bytes).decode("utf-8")

    # GPT-4o Vision API 호출 (Text + Image)
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": "gpt-4.1",
            "messages": [
                {"role": "system", "content": "당신은 이미지 분석 도우미입니다. 주어진 이미지를 한국어로 1~2문장으로 간결하게 설명해주세요."},
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_image}"}},
                        {"type": "text", "text": "이 이미지를 분석해서 가게일 경우 가게의 인테리어, 분위기, 뷰, 특징을, 특정 상품일 경우 해당 상품의 정보, 이미지 속 상품의 긍정적인 특징을 홍보용으로 작성해줘"}
                    ]
                }
            ],
            "max_tokens": 200
        }
    )

    if response.status_code != 200:
        print("이미지 분석 실패:", response.text)
        return ""

    result = response.json()
    description = result["choices"][0]["message"]["content"].strip()
    return description

def build_chain():
    system_message = load_system_message("src/prompts/image_prompt.txt")
    template = system_message + """

    플랫폼: {platform}
    아이템: {item}
    포맷: {format}
    연령대: {age}
    성별: {gender}
    외부 데이터: {external}
    유저 요청: {user_request}
    가게 정보: {store_description}
    위 내용을 참고하여, 반드시 image_prompt.txt에서 제시된 포맷과 룰을 적용해 **최종 DALL·E 프롬프트만** 작성해주세요.
    **All Korean text in the comic must be fully rendered, clearly legible, and not broken, distorted, or replaced with placeholder symbols.**
    설명이나 지침은 넣지 말고, 결과 프롬프트만 주세요.
    """
    prompt = PromptTemplate(
        input_variables=["platform", "item", "format", "age", "gender", "external", "user_request", "store_description", "user_image_description"],
        template=template
    )
    llm = ChatOpenAI(model="gpt-4.1", temperature=0.7)
    return prompt, llm

def generate_marketing_image(content: Content, db: Session) -> str:
    store_name, store_address, store_description = get_store_info(db, content.user_id)
    if not store_name or not store_address:
        raise Exception("대표 가게 정보가 없습니다.")

    platform_name = get_text_by_id(db, Platform, Platform.platform_id, content.platform_id, "platform_name")
    item_name = get_text_by_id(db, Item, Item.item_id, content.item_id, "item_name")
    format_name = get_text_by_id(db, Format, Format.format_id, content.format_id, "format_name")
    age_name = get_text_by_id(db, Age, Age.age_id, content.age_id, "age_category")
    gender_name = get_text_by_id(db, Gender, Gender.gender_id, content.gender_id, "gender_category")
    external_data_names = [e.external_data_name for e in content.external_data_list]
    print("🧪 external_data_names:", external_data_names)
    external_data_names_str = ", ".join(external_data_names) if external_data_names else "없음"

    for name, value in [("platform", platform_name), ("item", item_name), ("format", format_name),
                        ("age", age_name), ("gender", gender_name), ("external", external_data_names_str)]:
        if not value:
            raise Exception(f"{name} 값이 비어 있습니다. DB를 확인해주세요.")

    external_data_text = get_external_data_multi(external_data_names, store_address, store_name)

    user_image_description = describe_user_image(content)
    if user_image_description:
        external_data_text += f"\n유저 제공 이미지: {user_image_description}"

    print("\n=== 선택된 카테고리 정보 ===")
    print(f"Platform: {platform_name}")
    print(f"Item: {item_name}")
    print(f"Format: {format_name}")
    print(f"Age: {age_name}")
    print(f"Gender: {gender_name}")
    print(f"External: {external_data_text}")
    print(f"User Request: {content.request_text}")
    print("===========================\n")

    prompt, llm = build_chain()
    formatted_prompt = prompt.format(
        platform=platform_name,
        item=item_name,
        format=format_name,
        age=age_name,
        gender=gender_name,
        external=external_data_text,
        user_request=content.request_text,
        store_description=store_description,
        user_image_description=user_image_description
    )

    try:
        result = llm.invoke(formatted_prompt)
        print("🧠 GPT 응답 result 타입:", type(result))
        print("🧠 GPT 응답 result 내용:", result)
    except Exception as e:
        import traceback
        print("❌ GPT invoke 중 예외 발생:", e)
        traceback.print_exc()
        raise Exception("GPT 호출 실패: " + str(e))

    if hasattr(result, "content"):
        final_prompt = result.content.strip()
    elif isinstance(result, str):
        final_prompt = result.strip()
    else:
        raise Exception("GPT 응답 파싱 실패: 응답 구조가 맞지 않습니다.")

    if len(final_prompt) > MAX_PROMPT_LENGTH:
        final_prompt = final_prompt[:MAX_PROMPT_LENGTH]

    print("\n=== 최종 GPT 이미지 프롬프트 ===")
    print(final_prompt)
    print("================================\n")

    dalle_res = requests.post(
        "https://api.openai.com/v1/images/generations",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": "gpt-image-1",
            "prompt": final_prompt,
            "n": 1,
            "size": "1024x1024",
            "quality": "medium"
        }
    )


    if dalle_res.status_code != 200:
        raise Exception(f"GPT Image 1 API 호출 실패: {dalle_res.status_code}, {dalle_res.text}")

    response_json = dalle_res.json()
    if "data" not in response_json or not response_json["data"]:
        raise Exception("GPT Image 1 응답에 이미지 데이터 없음")

    image_data = response_json["data"][0]
    filename = f"generated_images/content_{content.content_id}.png"
    dir_path = os.path.dirname(filename)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)

    if "url" in image_data:
        # URL 방식 (거의 안 나옴, fallback용)
        image_url = image_data["url"]
        image_bytes = requests.get(image_url).content
        with open(filename, 'wb') as f:
            f.write(image_bytes)
    elif "b64_json" in image_data:
        # Base64 이미지 처리
        image_bytes = base64.b64decode(image_data["b64_json"])

        print("📁 현재 작업 디렉토리:", os.getcwd())
        print("📁 이미지 저장 경로:", filename)

        with open(filename, 'wb') as f:
            f.write(image_bytes)
        image_url = filename
    else:
        raise Exception("GPT Image 1 응답 형식이 예상과 다릅니다")

    content.image_url = image_url
    db.commit()
    return image_url
