from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.models import User, Store
from src.schemas import StoreOut, StoreUpdate, NicknameUpdate, DefaultStoreUpdate
from src.dependencies import get_current_user

router = APIRouter(prefix="/stores", tags=["stores"])


# [1] 닉네임 수정
@router.patch("/nickname", summary="닉네임 수정")
def update_nickname(
        body: NicknameUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    current_user.nickname = body.nickname
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


# [3] 가게 상세 조회
@router.get("/{store_id}", response_model=StoreOut, summary="가게 상세 정보 조회")
def get_store_detail(
        store_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    store = db.query(Store).filter(Store.store_id == store_id, Store.owner_id == current_user.user_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="가게를 찾을 수 없습니다.")
    return store


# [4] 가게 정보 수정
@router.patch("/{store_id}", summary="가게 정보 수정")
def update_store(
        store_id: int,
        body: StoreUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    store = db.query(Store).filter(Store.store_id == store_id, Store.owner_id == current_user.user_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="가게를 찾을 수 없습니다.")

    store.name = body.name
    store.phone = body.phone
    store.description = body.description
    db.commit()
    return {"message": "가게 정보가 수정되었습니다."}


# [5] 가게 삭제
@router.delete("/{store_id}", summary="가게 삭제")
def delete_store(
        store_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    store = db.query(Store).filter(Store.store_id == store_id, Store.owner_id == current_user.user_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="가게를 찾을 수 없습니다.")

    db.delete(store)
    db.commit()
    return {"message": "가게가 삭제되었습니다."}


# [6] 대표 가게 설정
@router.patch("/set-default", summary="대표 가게 설정")
def set_default_store(
        body: DefaultStoreUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    store = db.query(Store).filter(Store.store_id == body.store_id, Store.owner_id == current_user.user_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="가게를 찾을 수 없습니다.")

    current_user.default_store_id = body.store_id
    db.commit()
    return {"message": "대표 가게가 설정되었습니다."}
