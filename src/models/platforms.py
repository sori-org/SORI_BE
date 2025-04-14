from sqlalchemy import Column, Integer, String, Boolean
from src.database.database import Base

class Platforms(Base):
    __tablename__ = "platforms"

    platform_id = Column(Integer, primary_key=True)
    platform_name = Column(String(100), nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)