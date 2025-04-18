from fastapi import APIRouter, Depends, HTTPException, Header
from typing import Optional
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.services.auth.dependencies import get_current_user
from src.services.auth.kakao_unlink import unlink_kakao_user  # 카카오 unlink 함수
from src.schemas.users import UserOut
from src.models.users import User
from src.models.accounts import Account

router = APIRouter(prefix="/users", tags=["User"])

# 🔍 현재 로그인된 유저 정보 반환
@router.get("/me", response_model=UserOut)
def get_my_info(
    current_user=Depends(get_current_user)
):
    return current_user


@router.delete("/me")
def delete_my_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    kakao_access_token: Optional[str] = Header(None, alias="X-Kakao-Access-Token")  # 이거!!
):

    print("🧪 받은 kakao_access_token:", kakao_access_token)  # 여기에 찍히는지 확인
    try:
        unlink_kakao_user(kakao_access_token)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"카카오 unlink 실패: {e}")

    db.delete(current_user)
    db.commit()

    return {"message": "회원탈퇴 완료"}