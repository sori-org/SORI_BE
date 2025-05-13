from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.db.database import SessionLocal
from src import models, schemas
from src.schemas.stores import StoreCreate, StoreOut

router = APIRouter(prefix="/stores", tags=["가게/대표가게 등록 및 조회, 수정, 삭제"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=schemas.store.StoreOut)
def create_store(store: schemas.store.StoreCreate, db: Session = Depends(get_db)):
    try:
        user = db.query(models.user.User).filter(models.user.User.id == store.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

        existing = db.query(models.store.Store).filter(
            models.store.Store.registration_number == store.registration_number
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="이미 등록된 가게입니다.")

        db_store = models.store.Store(**store.dict())
        db.add(db_store)
        db.commit()
        db.refresh(db_store)
        return db_store

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"가게 등록 중 오류 발생: {str(e)}")
