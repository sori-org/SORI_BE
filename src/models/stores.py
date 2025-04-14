from sqlalchemy import Column, BigInteger, ForeignKey, String, Text
from src.database.database import Base

class Stores(Base):
    __tablename__ = "stores"

    store_id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    store_name = Column(String(100), nullable=False)
    store_phone_number = Column(String(11), nullable=False)
    store_location = Column(String(100), nullable=False)

