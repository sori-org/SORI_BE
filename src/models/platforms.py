from sqlalchemy import Column, Integer, String, Boolean
from src.db.database import Base

class Platform(Base):
    __tablename__ = "platforms"

    platform_id = Column(Integer, primary_key=True, autoincrement=True)
    platform_name = Column(String(100), nullable=False)

