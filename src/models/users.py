from sqlalchemy import BigInteger, Column, String
from src.db.database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
