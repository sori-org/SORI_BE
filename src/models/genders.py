from sqlalchemy import Column, Integer, String
from src.database.database import Base

class Gender(Base):
    __tablename__ = "genders"

    gender_id = Column(Integer, primary_key=True, autoincrement=True)
    gender_category = Column(String(20), nullable=False)