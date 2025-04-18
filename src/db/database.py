from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
from dotenv import load_dotenv

# .env 로드
load_dotenv(dotenv_path=".env")

# .env에서 직접 DATABASE_URL 가져오기
DATABASE_URL = os.getenv("DATABASE_URL")

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
