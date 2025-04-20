from sqlalchemy.orm import Session
from src.models.stores import Store
from src.schemas.stores import StoreCreate

def create_store(db: Session, store_data: StoreCreate):
    store = Store(**store_data.dict())
    db.add(store)
    db.commit()
    db.refresh(store)
    return store
