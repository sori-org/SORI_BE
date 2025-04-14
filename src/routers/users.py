from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database.database import get_db
from src.services.auth.dependencies import get_current_user
from src.services.auth.kakao_auth import unlink_kakao_user  # 카카오 unlink 함수
from src.schemas.users import UserOut

router = APIRouter(prefix="/users", tags=["User"])

# 🔍 현재 로그인된 유저 정보 반환
@router.get("/me", response_model=UserOut)
def get_my_info(
    current_user=Depends(get_current_user)
):
    return current_user


# ❌ 회원 탈퇴 (논리 삭제 + 카카오 unlink)
@router.delete("/me")
def delete_my_account(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 논리 삭제
    current_user.is_deleted = True
    db.commit()

    # 카카오 unlink (access_token 저장돼 있어야 함)
    try:
        unlink_kakao_user(current_user.access_token)  # 이 필드는 실제로 저장돼 있어야 함
    except Exception:
        raise HTTPException(status_code=500, detail="카카오 unlink 실패")

    return {"message": "회원탈퇴 완료"}
