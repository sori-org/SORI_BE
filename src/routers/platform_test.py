from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.models.platforms import Platform


router = APIRouter(
    prefix="/api/platforms",
    tags=["Platforms"]
)

# [0] 플랫폼 서버 연결 테스트
@router.get("/ping", summary="DB 연결 테스트용", description="DB 연결 상태를 확인하고, 샘플 플랫폼 이름 반환.")
def ping_platforms(
    db: Session = Depends(get_db)
):
    platform = db.query(Platform).first()
    return {
        "db_connected": True,
        "sample_platform": platform.platform_name if platform else None
    }
