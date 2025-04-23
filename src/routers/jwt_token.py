from fastapi import APIRouter
from pydantic import BaseModel
from src.services.auth.jwt_handler import create_jwt_token

router = APIRouter(prefix="/auth", tags=["Auth"])


class TokenRequest(BaseModel):
    user_id: int


@router.post("/jwt/generate", summary="JWT 토큰 발급 (user_id 입력)")
def generate_token(payload: TokenRequest):
    jwt_token = create_jwt_token(data={"sub": str(payload.user_id)})
    return {"jwt_token": jwt_token}