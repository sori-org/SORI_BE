from sqlalchemy import Integer, Column, ForeignKey, String, Text
from src.db.database import Base

class ExternalData(Base):
    __tablename__ = "external_data"
    external_data_id = Column(Integer, primary_key=True, autoincrement=True)
    external_data_name = Column(String(100), nullable=False)
