from fastapi import APIRouter, Depends, HTTPException, Header
from typing import Optional
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.services.auth.dependencies import get_current_user
from src.services.auth.kakao_unlink import unlink_kakao_user  # 카카오 unlink 함수
from src.schemas.users import UserOut, NicknameUpdate
from src.schemas.stores import StoreBase
from src.schemas.store_schema import StoreOut
from src.models.users import User
from src.models.accounts import Account


router = APIRouter(prefix="/user", tags=["User"])

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

    account = db.query(Account).filter(Account.account_id == current_user.account_id).first()

    db.delete(current_user)
    if account:
        db.delete(account)
    db.commit()

    return {"message": "회원탈퇴 완료"}


# [1] 닉네임 수정
@router.patch("/nickname", summary="닉네임 수정")
def update_nickname(
        body: NicknameUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    current_user.display_name = body.displayName
    db.commit()
    return {"message": "닉네임이 수정되었습니다."}


# [2] 소유 가게 목록 조회
@router.get("/my", response_model=list[StoreOut], summary="내 소유 가게 목록 조회")
def get_my_stores(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    stores = db.query(Store).filter(Store.owner_id == current_user.user_id).all()
    return stores
