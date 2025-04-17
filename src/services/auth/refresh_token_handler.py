from sqlalchemy.orm import Session
from src.models.accounts import Account

def save_refresh_token(db: Session, account_id: int, refresh_token: str):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise ValueError("Account not found")

    account.refresh_token = refresh_token
    db.commit()
    db.refresh(account)
    return account

def delete_refresh_token(db: Session, account_id: int):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise ValueError("Account not found")

    account.refresh_token = None
    db.commit()
    db.refresh(account)
    return account
