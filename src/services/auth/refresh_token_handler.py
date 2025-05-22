from sqlalchemy.orm import Session
from src.models.accounts import Account
import hashlib

def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

def save_refresh_token(db: Session, account_id: int, refresh_token: str):
    account = db.query(Account).filter(Account.account_id == account_id).first()
    if not account:
        raise ValueError("Account not found")

    hashed_token = hash_token(refresh_token)
    account.refresh_token = hashed_token
    db.commit()
    db.refresh(account)
    return account

def delete_refresh_token(db: Session, account_id: int):
    account = db.query(Account).filter(Account.account_id == account_id).first()
    if not account:
        raise ValueError("Account not found")

    account.refresh_token = None
    db.commit()
    db.refresh(account)
    return account

def verify_refresh_token(db: Session, account_id: int, received_token: str) -> bool:
    account = db.query(Account).filter(Account.account_id == account_id).first()
    if not account or not account.refresh_token:
        return False
    return account.refresh_token == hash_token(received_token)