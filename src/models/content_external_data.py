from sqlalchemy import Table, Column, ForeignKey, BigInteger, Integer
from src.db.database import Base

content_external_data = Table(
    "content_external_data",
    Base.metadata,
    Column("content_id", BigInteger, ForeignKey("contents.content_id", ondelete="CASCADE"), primary_key=True),
    Column("external_data_id", Integer, ForeignKey("external_data.external_data_id", ondelete="CASCADE"), primary_key=True),
)
