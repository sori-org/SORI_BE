from sqlalchemy import Column, BigInteger, Boolean
from src.database.database import Base

class Accounts(Base):
    __tablename__ = "accounts"

    account_id = Column(BigInteger, primary_key=True, autoincrement=True)
    kakao_id = Column(BigInteger, unique=True, index=True, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)