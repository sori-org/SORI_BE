from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.models.users import User
from src.schemas.users import NicknameUpdate
from src.models.stores import Store
from src.services.auth.dependencies import get_current_user

router = APIRouter(
    prefix="/api/users",
    tags=["Users"]
)

# [0] 로그인 정보 조회
@router.get("/me", summary="로그인 정보(프로필) 조회 API", description="현재 로그인한 사용자의 정보 조회.")
def read_user_me(
    current_user: User = Depends(get_current_user)
):
    return current_user


# [1] 내 계정 삭제 (회원 탈퇴)
@router.delete("/me", summary="회원 탈퇴 API", description="현재 로그인한 사용자의 계정을 삭제.")
def delete_user_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db.delete(current_user)
    db.commit()
    return {"message": "회원 탈퇴가 완료되었습니다."}


# [2] 내 닉네임 수정
@router.patch("/me/nickname", summary="닉네임 수정 API", description="현재 로그인한 사용자의 닉네임 수정.")
def update_user_nickname(
    body: NicknameUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    current_user.nickname = body.nickname
    db.commit()
    return {"message": "닉네임이 수정되었습니다."}


# [3] 내가 등록한 가게 목록 조회
@router.get("/me/stores", summary="가게 목록 조회 API", description="현재 로그인한 사용자가 등록한 가게 목록 조회.")
def get_my_stores(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stores = db.query(Store).filter(Store.user_id == current_user.user_id).all()
    return stores
