from sqlalchemy import Column, BigInteger, ForeignKey, String, Text, relationship
from src.db.database import Base

class Store(Base):
    __tablename__ = "stores"

    store_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    store_name = Column(String(100), nullable=False)
    store_address = Column(String(255), nullable=True)
    store_category = Column(String(255), nullable=True)
    store_phone = Column(String(20), nullable=True)
    store_description = Column(String(500), nullable=True)

    user = relationship("User", back_populates="stores")
