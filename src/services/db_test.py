from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from src.database.database import get_db
from src.models.users import Users

router = APIRouter()

@router.get("/ping-db")
def ping_db(db: Session = Depends(get_db)):
    user = db.query(Users).first()  # 아무 유저나 하나
    return {"db_connected": True, "sample_user": user.display_name if user else None}