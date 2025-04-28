from fastapi import APIRouter
from pydantic import BaseModel
from src.services.auth.jwt_handler import create_jwt_token

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)

class TokenRequest(BaseModel):
    user_id: int

# [0] JWT 토큰 발급 (user_id 입력)
@router.post("/jwt", summary="JWT 토큰 발급", description="user_id를 입력받아서 JWT 토큰 생성.")
def generate_token(payload: TokenRequest):
    jwt_token = create_jwt_token(data={"sub": str(payload.user_id)})
    return {"jwt_token": jwt_token}
