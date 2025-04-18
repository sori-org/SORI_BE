from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.models.users import User

router = APIRouter()

@router.get("/ping-db")
def ping_db(db: Session = Depends(get_db)):
    user = db.query(User).first()  # 아무 유저나 하나
    return {"db_connected": True, "sample_user": user.display_name if user else None}