from fastapi import APIRouter, Depends, HTTPException, Body, Request
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from src.services.kakao_user_info import get_kakao_user_info, extract_user_info
from src.services.kakao_user_register import get_or_create_kakao_user
from src.database.database import get_db
from src.services.auth.jwt_handler import create_access_token

router = APIRouter(prefix="/kakao", tags=["Kakao Login"])
load_dotenv()

KAKAO_TOKEN_URL = "https://kauth.kakao.com/oauth/token"
REST_API_KEY = os.getenv("KAKAO_REST_API_KEY")

class KakaoCallbackPayload(BaseModel):
    code: str
    redirectUri: str


@router.api_route("/callback", methods=["GET", "POST", "OPTIONS"])
async def kakao_login(
    request: Request,
    db: Session = Depends(get_db)
):
    if request.method == "GET": # GET
        code = request.query_params.get("code")
        redirect_uri = request.query_params.get("redirectUri")
    else:  # POST
        body = await request.json()
        code = body.get("code")
        redirect_uri = body.get("redirectUri")

    if not code or not redirect_uri:
        raise HTTPException(status_code=400, detail="code 또는 redirectUri 누락")

    # 1. 인가코드로 토큰 요청
    data = {
        "grant_type": "authorization_code",
        "client_id": REST_API_KEY,
        "redirect_uri": redirect_uri,
        "code": code,
    }
    print(f"🔑 인가 코드 수신: {code}")

    print("🔍 TOKEN 요청 payload:", data)

    token_res = requests.post(KAKAO_TOKEN_URL, data=data)
    if token_res.status_code != 200:
        raise HTTPException(status_code=400, detail="카카오 토큰 요청 실패")

    print("🔍 응답 상태코드:", token_res.status_code)
    print("🔍 응답 본문:", token_res.text)

    access_token = token_res.json().get("access_token")

    # 2. 토큰으로 유저 정보 요청
    kakao_user = get_kakao_user_info(access_token)
    user_data = extract_user_info(kakao_user)

    # DB에 유저 저장 or 조회
    user, is_new = get_or_create_kakao_user(db, user_data, access_token)

    # ✅ 3. JWT 발급
    jwt_token = create_access_token(data={"sub": str(user.user_id)})
    print("🔍 응답 본문:", jwt_token)

    return {
        "user": user_data,
        "jwt": jwt_token
    }
