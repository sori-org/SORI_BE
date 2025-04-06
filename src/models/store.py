from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database.database import Base
from datetime import datetime

class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    owner_id = Column(Integer, ForeignKey("users.id"))  # FK
    owner_name = Column(String, nullable=False)
    owner_phone = Column(String, nullable=False)

    store_phone = Column(String, nullable=False)
    registration_number = Column(String, nullable=False, unique=True)
    address = Column(String, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 관계
    owner = relationship("User", back_populates="stores")
