from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database.database import get_db
from src.models.platforms import Platform

router = APIRouter()

@router.get("/ping-platforms")
def ping_platforms(db: Session = Depends(get_db)):
    platform = db.query(Platforms).first()
    return {
        "db_connected": True,
        "sample_platform": platform.platform_name if platform else None
    }