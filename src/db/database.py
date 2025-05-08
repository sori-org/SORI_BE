from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
from dotenv import load_dotenv

# .env 로드
load_dotenv(dotenv_path=".env")

# .env에서 DATABASE_URL 한 줄로 불러오기
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL 환경변수가 설정되지 않았습니다.")

# SQLAlchemy 구성
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 의존성 주입 함수
def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from src.models import external_data, contents, stores, users