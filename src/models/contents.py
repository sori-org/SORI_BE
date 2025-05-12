from sqlalchemy import BigInteger, Column, ForeignKey, Integer, String, TIMESTAMP
from src.db.database import Base
from sqlalchemy.sql import func


class Content(Base):
    __tablename__ = "contents"

    content_id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    platform_id = Column(Integer, ForeignKey("platforms.platform_id"), nullable=True)
    format_id = Column(Integer, ForeignKey("formats.format_id"), nullable=True)
    item_id = Column(Integer, ForeignKey("items.item_id"), nullable=True)
    age_id = Column(Integer, ForeignKey("ages.age_id"), nullable=True)
    gender_id = Column(Integer, ForeignKey("genders.gender_id"), nullable=True)
    external_data_id = Column(Integer, ForeignKey("external_data.external_data_id"), nullable=True)
    image_url = Column(String(2048), nullable=True)
    request_text = Column(String(500), nullable=True)
    user_image_url = Column(String(500), nullable=True)
    result_text = Column(String(2000), nullable=True)
    result_hashtag = Column(String(100), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    status = Column(String, default="pending")
    store_id = Column(BigInteger, ForeignKey("stores.store_id"), nullable=True)
