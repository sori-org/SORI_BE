from sqlalchemy import Column, BigInteger, Boolean, String
from src.db.database import Base

class Account(Base):
    __tablename__ = "accounts"

    account_id = Column(BigInteger, primary_key=True, autoincrement=True)
    kakao_id = Column(BigInteger, unique=True, index=True, nullable=False)
    kakao_refresh_token = Column(String(512), nullable=True)
    jwt_refresh_token = Column(String(512), nullable=True)