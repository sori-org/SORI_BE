
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.schemas.store_schema import StoreCreate, StoreResponse, StoreOut, StoreUpdate
from src.schemas.users import NicknameUpdate, DefaultStoreUpdate
from src.crud.store import create_store
from src.db.database import get_db
from src.models.users import User
from src.models.stores import Store
from src.services.auth.dependencies import get_current_user


router = APIRouter(tags=["Stores"])


# [0] 가게 등록
@router.post("/register", response_model=StoreResponse)
def register_store(store: StoreCreate, db: Session = Depends(get_db)):
    existing_store = db.query(Store).filter(
        Store.user_id == store.user_id,
        Store.store_name == store.store_name,
        Store.store_address == store.store_address
    ).first()

    if existing_store:
        raise HTTPException(
            status_code=400,
            detail="해당 유저가 동일한 가게 정보를 이미 등록했습니다."
        )

    new_store = create_store(db, store)

    user = db.query(User).filter(User.user_id == store.user_id).first()
    is_main = False
    if user and user.main_store_id is None:
        user.main_store_id = new_store.store_id
        db.commit()
        is_main = True

    return {
        "store_id": new_store.store_id,
        "store_name": new_store.store_name,
        "store_address": new_store.store_address,
        "user_id": new_store.user_id,
        "message": "대표 가게로 등록되었습니다." if is_main else "가게가 정상적으로 등록되었습니다."
    }




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
