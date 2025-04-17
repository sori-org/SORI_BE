from sqlalchemy import Column, Integer, String
from src.database.database import Base

class Format(Base):
    __tablename__ = "formats"

    format_id = Column(Integer, primary_key=True, autoincrement=True)
    format_name = Column(String(50), nullable=False)