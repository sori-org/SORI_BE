from sqlalchemy import BigInteger, Column, ForeignKey, String, Text
from src.db.database import Base

class ExternalData(Base):
    __tablename__ = "external_data"

    data_id = Column(BigInteger, primary_key=True, autoincrement=True)
    request_id = Column(BigInteger, ForeignKey("content_requests.request_id", ondelete="CASCADE"), nullable=False)
    source = Column(String(100), nullable=False)
    data_type = Column(String(100), nullable=False)
    content = Column(Text, nullable=True)
