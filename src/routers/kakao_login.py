from fastapi import APIRouter, Depends, HTTPException, Body, Request, Response
from fastapi.responses import JSONResponse
from datetime import timedelta
from pydantic import BaseModel, Field
import requests, os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from src.models.accounts import Account
from src.models.users import User
from src.schemas.users import UserOut
from src.services.kakao_user_info import get_kakao_user_info, extract_user_info
from src.services.kakao_user_register import get_or_create_kakao_user
from src.db.database import get_db
from src.services.auth.jwt_handler import create_jwt_token, create_jwt_refresh_token
from src.services.auth.refresh_token_handler import save_refresh_token
from src.services.auth.dependencies import get_current_user


router = APIRouter(
    prefix="/api/auth/kakao",
    tags=["로그인"]
)

load_dotenv()

KAKAO_TOKEN_URL = "https://kauth.kakao.com/oauth/token"
REST_API_KEY = os.getenv("KAKAO_REST_API_KEY")

class KakaoCallbackPayload(BaseModel):
    code: str = Field(..., example="abc123인가코드")
    redirectUri: str = Field(..., example="http://yourserver.com/api/auth/kakao/callback")

def login(code: str, redirect_uri: str, db: Session):
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
    jwt_refresh_token = create_jwt_refresh_token(data={"sub": str(user.user_id)})

    return user, jwt_token, jwt_refresh_token



# [0] 카카오 인가 코드 수신 (GET 방식)
@router.get("/callback")
async def kakao_callback_get(code: str, db: Session = Depends(get_db)):
    redirect_uri = os.getenv("KAKAO_REDIRECT_URI")
    user, jwt_access_token, jwt_refresh_token = login(code, redirect_uri, db)
    response = JSONResponse(content={
        "jwt_token": jwt_access_token,
        "user": UserOut.from_orm(user).dict(),
    })
    response.set_cookie(
        key="refresh_token",
        value=jwt_refresh_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=60 * 60 * 24 * 14,
        path="/"
    )
    return response

# [1] 카카오 인가 코드 수신 (POST 방식)
@router.post("/callback")
async def kakao_callback_post(
    payload: KakaoCallbackPayload = Body(...),
    db: Session = Depends(get_db)
):
    user, jwt_access_token, jwt_refresh_token = login(payload.code, payload.redirectUri, db)
    response = JSONResponse(content={
        "jwt_token": jwt_access_token,
        "user": UserOut.from_orm(user).dict(),
    })
    response.set_cookie(
        key="refresh_token",
        value=jwt_refresh_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=60 * 60 * 24 * 14,
        path="/"
    )
    return response
# [2] 카카오 로그아웃
@router.post("/logout", summary="로그아웃", description="db와 쿠키에 저장된 refresh_token 삭제")
def logout(
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    account = db.query(Account).filter(Account.account_id == current_user.account_id).first()
    if account:
        account.kakao_refresh_token = None
        db.commit()
    response.delete_cookie("refresh_token")
    return {"message": "로그아웃 완료"}