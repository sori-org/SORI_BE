from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database.database import get_db
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
    db: Session = Depends(get_db)
):
    print("🔥 current_user:", current_user)
    print("🔥 account_id:", current_user.account_id)

    account = db.query(Account).filter_by(account_id=current_user.account_id).first()
    print("🔥 account:", account)

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    print("🔥 access_token:", account.access_token)

    try:
        unlink_kakao_user(account.access_token)
    except Exception as e:
        print("❌ unlink 실패:", e)
        raise HTTPException(status_code=500, detail=f"카카오 unlink 실패: {e}")

    db.delete(current_user)
    db.delete(account)
    db.commit()

    return {"message": "회원탈퇴 완료"}