from sqlalchemy import BigInteger, Column, ForeignKey, Integer, String, TIMESTAMP
from src.db.database import Base
from sqlalchemy.sql import func

class Content(Base):
    __tablename__ = "contents"

    content_id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    platform = Column(String(20), nullable=False)
    request_id = Column(BigInteger, ForeignKey("content_requests.request_id", ondelete="CASCADE"), nullable=False)
    result_id = Column(BigInteger, ForeignKey("content_results.result_id", ondelete="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
