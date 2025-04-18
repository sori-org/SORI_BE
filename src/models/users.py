from sqlalchemy import Column, BigInteger, String, ForeignKey, Text
from src.db.database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    account_id = Column(BigInteger, ForeignKey("accounts.account_id", ondelete="CASCADE"), nullable=False)
    main_store_id = Column(
        BigInteger,
        ForeignKey("stores.store_id", ondelete="SET NULL", use_alter=True, name="fk_users_main_store_id"),
        nullable=True
    )
    display_name = Column(String(20), nullable=False)
    profile_image = Column(String(2048), nullable=True)