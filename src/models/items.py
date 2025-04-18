from sqlalchemy import Column, Integer, String
from src.db.database import Base

class Item(Base):
    __tablename__ = "items"

    item_id = Column(Integer, primary_key=True, autoincrement=True)
    item_name = Column(String(100), nullable=False)
