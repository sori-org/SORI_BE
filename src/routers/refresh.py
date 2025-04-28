from fastapi import APIRouter, Depends, Cookie, HTTPException
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.models.accounts import Account
from src.services.auth.refresh_token_handler import hash_token
import requests
import os

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)


# [0] 카카오 access_token 재발급
@router.post("/refresh", summary="카카오 access_token 재발급", description="저장된 refresh_token을 사용해서 새로운 access_token을 발급받음.")
def refresh_kakao_access_token(
    refresh_token: str = Cookie(...),
    db: Session = Depends(get_db)
):
    hashed = hash_token(refresh_token)
    account = db.query(Account).filter(Account.refresh_token == hashed).first()

    if not account:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    data = {
        "grant_type": "refresh_token",
        "client_id": os.getenv("KAKAO_REST_API_KEY"),
        "refresh_token": refresh_token
    }

    token_res = requests.post("https://kauth.kakao.com/oauth/token", data=data)
    if token_res.status_code != 200:
        raise HTTPException(status_code=400, detail="카카오 access_token 갱신 실패")

    new_access_token = token_res.json().get("access_token")

    if not new_access_token:
        raise HTTPException(status_code=500, detail="access_token 누락")

    return {"access_token": new_access_token}
