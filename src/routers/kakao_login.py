from fastapi import APIRouter, Depends, HTTPException, Body, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import requests, os
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from src.schemas.users import UserOut
from src.services.kakao_user_info import get_kakao_user_info, extract_user_info
from src.services.kakao_user_register import get_or_create_kakao_user
from src.db.database import get_db
from src.services.auth.jwt_handler import create_jwt_token
from src.services.auth.refresh_token_handler import save_refresh_token

router = APIRouter(prefix="/kakao", tags=["Kakao Login"])
load_dotenv()

KAKAO_TOKEN_URL = "https://kauth.kakao.com/oauth/token"
REST_API_KEY = os.getenv("KAKAO_REST_API_KEY")

class KakaoCallbackPayload(BaseModel):
    code: str = Field(..., example="abc123인가코드")
    redirectUri: str = Field(..., example="http://ec2-44-208-199-212.compute-1.amazonaws.com/api/kakao/callback")

def process_kakao_login(code: str, redirect_uri: str, db: Session):
    data = {
        "grant_type": "authorization_code",
        "client_id": REST_API_KEY,
        "redirect_uri": redirect_uri,
        "code": code,
    }

    token_res = requests.post(KAKAO_TOKEN_URL, data=data)
    if token_res.status_code != 200:
        raise HTTPException(status_code=400, detail=f"카카오 토큰 요청 실패: {token_res.text}")

    kakao_token_data = token_res.json()
    kakao_access_token = kakao_token_data.get("access_token")
    kakao_refresh_token = kakao_token_data.get("refresh_token")

    kakao_user = get_kakao_user_info(kakao_access_token)
    user_data = extract_user_info(kakao_user)
    user, is_new = get_or_create_kakao_user(db, user_data, kakao_access_token)

    if kakao_refresh_token:
        save_refresh_token(db, user.account_id, kakao_refresh_token)

    jwt_token = create_jwt_token(data={"sub": str(user.user_id)})

    response = JSONResponse(content={
        "jwt_token": jwt_token,
        "user": UserOut.from_orm(user).dict(),
    })

    if kakao_refresh_token:
        response.set_cookie(
            key="refresh_token",
            value=kakao_refresh_token,
            httponly=True,
            secure=True,
            samesite="Lax",
            max_age=60 * 60 * 24 * 14
        )
    return response

@router.get("/callback")
async def kakao_callback_get(code: str, db: Session = Depends(get_db)):
    redirect_uri = os.getenv("KAKAO_REDIRECT_URI")
    return process_kakao_login(code, redirect_uri, db)

@router.post("/callback")
async def kakao_callback_post(payload: KakaoCallbackPayload = Body(...), db: Session = Depends(get_db)):
    return process_kakao_login(payload.code, payload.redirectUri, db)

