from sqlalchemy import BigInteger, Column, ForeignKey, Integer, String, TIMESTAMP, Boolean
from sqlalchemy.orm import relationship
from src.db.database import Base
from sqlalchemy.sql import func
from src.models.content_external_data import content_external_data  # 중간 테이블 import

class Content(Base):
    __tablename__ = "contents"

    content_id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    platform_id = Column(Integer, ForeignKey("platforms.platform_id"), nullable=True)
    format_id = Column(Integer, ForeignKey("formats.format_id"), nullable=True)
    item_id = Column(Integer, ForeignKey("items.item_id"), nullable=True)
    age_id = Column(Integer, ForeignKey("ages.age_id"), nullable=True)
    gender_id = Column(Integer, ForeignKey("genders.gender_id"), nullable=True)
    image_url = Column(String(2048), nullable=True)
    request_text = Column(String(1000), nullable=True)
    user_image_url = Column(String(500), nullable=True)
    result_text = Column(String(3000), nullable=True)
    result_hashtag = Column(String(200), nullable=True)
    promotion_name = Column(String(150), nullable=True)
    is_downloaded = Column(Boolean, default=False)
    is_shared = Column(Boolean, default=False)
    is_copied = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    store_id = Column(BigInteger, ForeignKey("stores.store_id", ondelete="CASCADE"), nullable=True)

    external_data_list = relationship(
        "ExternalData",
        secondary=content_external_data,
        back_populates="contents"
    )
