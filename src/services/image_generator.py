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
from PIL import Image, ImageDraw, ImageFont
import base64
import requests
import os
import time
import re

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

def get_max_fontsize_for_box(text, font_path, box_width, box_height, max_font=150, min_font=50):
    # 박스 높이에 맞게 폰트 자동 조정
    for size in range(max_font, min_font-1, -2):
        font = ImageFont.truetype(font_path, size)
        bbox = font.getbbox(text)
        text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        if text_w <= box_width * 0.9 and text_h <= box_height * 0.8:
            return font
    return ImageFont.truetype(font_path, min_font)

def draw_ad_caption(im, caption, font_path):
    w, h = im.size
    CAPTION_HEIGHT = int(h * 0.18)  # 하단 18%
    draw = ImageDraw.Draw(im)

    # 하단 박스
    draw.rectangle([0, h-CAPTION_HEIGHT, w, h], fill=(0,0,0,220))  # 반투명 검정 등도 가능

    # 폰트 결정(박스에 맞춰 크게)
    font = get_max_fontsize_for_box(re.sub(r'<노란색>|</노란색>', '', caption), font_path, w, CAPTION_HEIGHT)
    bbox = draw.textbbox((0,0), re.sub(r'<노란색>|</노란색>', '', caption), font=font)
    text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (w - text_w) // 2
    y = h - CAPTION_HEIGHT + (CAPTION_HEIGHT - text_h)//2

    # 색 강조
    def draw_colored(draw, pos, text, font, base, highlight, stroke=4):
        cur = pos[0]
        for part in re.split(r'(<노란색>.*?</노란색>)', text):
            if part.startswith('<노란색>') and part.endswith('</노란색>'):
                t = part[5:-6]
                color = highlight
            else:
                t = part
                color = base
            draw.text((cur, pos[1]), t, font=font, fill=color, stroke_width=stroke, stroke_fill=(0,0,0))
            cur += font.getlength(t)
    # 예시: draw_colored(draw, (x, y), caption, font, (255,255,255), (255,212,0), 4)
    draw_colored(draw, (x, y), caption, font, (255,255,255), (255,212,0), 4)

    return im

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

def build_caption_llm():
    # 시스템 메시지: 만화 컷, 자막 모두를 지원하도록 범용화
    system_message = (
        "너는 마케팅 만화/이미지 자막 생성 도우미다. "
        "입력된 정보를 바탕으로 20자 이내의 한글 자막이나 대사를 만들어라. "
        "강조 단어는 <노란색> ... </노란색> 태그로 감싼다. "
        "cut_toon(4컷 만화)일 경우, 각 컷마다 적절한 대사를 순서대로 줄바꿈해서 만들어줘."
    )
    llm = ChatOpenAI(model="gpt-4.1", temperature=0.7)
    return system_message, llm

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

    start_vision = time.time()
    user_image_description = describe_user_image(content)
    end_vision = time.time()
    print(f"이미지 설명(vision) 소요 시간: {end_vision - start_vision:.2f}초")

    if user_image_description:
        external_data_text += f"\n유저 제공 이미지: {user_image_description}"

    if format_name == "post_cover+text":
        # ... (생략)
        system_message, caption_llm = build_caption_llm()
        prompt = f"""아래 정보를 참고해서 20자 이내의 한글 자막을 만들어라.
        - 유저 요청: {content.request_text}
        - 가게 설명: {store_description}
        - 상품명: {item_name}
        - 외부 데이터: {external_data_text}
        """
        result = caption_llm.invoke(
            [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ]
        )
        caption_text = result.content.strip()

        # 이미지 경로 읽기
        image_path = content.user_image_url
        # 서버/로컬 경로 맞게 수정
        if image_path.startswith("/uploaded_images/"):
            image_path = image_path.replace("/uploaded_images/", "uploaded_images/")

        im = Image.open(image_path)
        if im.size != (1024, 1024):
            im = im.resize((1024, 1024), Image.LANCZOS)
        draw_ad_caption(im, caption_text, "./SB_aggro_B.ttf")

        # 저장
        save_path = f"generated_images/content_{content.content_id}.png"
        im.save(save_path)
        content.image_url = save_path
        db.commit()
        return save_path
    if format_name == "cut_toon":
        # ... (필요한 데이터 수집)
        system_message, caption_llm = build_caption_llm()
        prompt = f"""아래 정보를 참고해서 4컷 만화의 각 컷에 어울리는 대사를 4줄로 만들어라.
        - 유저 요청: {content.request_text}
        - 가게 설명: {store_description}
        - 상품명: {item_name}
        - 외부 데이터: {external_data_text}
        """
        result = caption_llm.invoke(
            [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ]
        )
        # result.content는 4줄 대사(각 컷별)
        cut_toon_captions = result.content.strip().split('\n')
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

    start_dalle = time.time()
    dalle_res = requests.post(
        "https://api.openai.com/v1/images/generations",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": "gpt-image-1",
            "prompt": final_prompt,
            "n": 1,
            "size": "1024x1024",
            "quality": "high"
        }
    )
    end_dalle = time.time()
    print(f"DALL·E 이미지 생성 소요 시간: {end_dalle - start_dalle:.2f}초")

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
