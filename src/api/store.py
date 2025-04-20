from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.schemas.stores import StoreCreate, StoreResponse
from src.crud.store import create_store
from src.db.database import get_db


router = APIRouter()

@router.post("/register", response_model=StoreResponse)
def register_store(store: StoreCreate, db: Session = Depends(get_db)):
    new_store = create_store(db, store)
    return new_store
