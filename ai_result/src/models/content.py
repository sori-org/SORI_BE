from sqlalchemy import Column, Integer, BigInteger, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base

class Content(Base):
    __tablename__ = "contents"

    content_id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=False)
    platform_id = Column(Integer, ForeignKey("platforms.platform_id"))
    item_id = Column(Integer, ForeignKey("items.item_id"))
    format_id = Column(Integer, ForeignKey("formats.format_id"))
    external_data_id = Column(Integer, ForeignKey("external_data.external_data_id"))
    gender_id = Column(Integer, ForeignKey("genders.gender_id"))
    age_id = Column(Integer, ForeignKey("ages.age_id"))

    request = Column(Text)
    result_image = Column(Text)
    text_and_hashtag = Column(Text)
