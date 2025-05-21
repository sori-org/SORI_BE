from sqlalchemy import Integer, Column, String
from sqlalchemy.orm import relationship
from src.db.database import Base
from src.models.content_external_data import content_external_data  # 중간 테이블 import

class ExternalData(Base):
    __tablename__ = "external_data"

    external_data_id = Column(Integer, primary_key=True, autoincrement=True)
    external_data_name = Column(String(100), nullable=False)

    contents = relationship(
        "Content",
        secondary=content_external_data,
        back_populates="external_data_list"
    )
