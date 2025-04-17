from sqlalchemy import Column, Integer, String
from src.database.database import Base

class Age(Base):
    __tablename__ = "ages"

    age_id = Column(Integer, primary_key=True, autoincrement=True)
    age_category = Column(String(20), nullable=False)
