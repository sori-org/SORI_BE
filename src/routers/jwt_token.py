from fastapi import APIRouter, Cookie, HTTPException
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from jose import jwt, JWTError
from src.services.auth.jwt_handler import create_jwt_token, create_jwt_refresh_token
import os

router = APIRouter(
    prefix="/api/auth",
    tags=["로그인"]
)

class TokenRequest(BaseModel):
    user_id: int

# [0] JWT 토큰 발급 (user_id 입력)
@router.post("/jwt", summary="JWT 토큰 발급", description="user_id를 입력받아서 JWT 토큰 생성.")
def generate_token(payload: TokenRequest):
    jwt_token = create_jwt_token(data={"sub": str(payload.user_id)})
    refresh_token = create_jwt_refresh_token(data={"sub": str(payload.user_id)})

    response = JSONResponse(content={"jwt_token": jwt_token})
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,      # 운영은 True, 개발환경 False
        samesite="lax",   # 필요에 따라 strict, none 등
        max_age=60*60*24*14,
        path="/"
    )
    return response

@router.post("/jwt-refresh", summary="JWT 리프레시 토큰으로 access_token 재발급")
def refresh_access_token(refresh_token: str = Cookie(None)):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="refresh_token이 필요합니다.")

    try:
        payload = jwt.decode(refresh_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="토큰에 user_id가 없습니다.")
    except JWTError:
        raise HTTPException(status_code=401, detail="refresh_token이 유효하지 않습니다.")

    # 새 access_token 발급
    new_access_token = create_jwt_token(data={"sub": str(user_id)})

    return {"jwt_token": new_access_token}