from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from database.database import get_db
from src.services.auth.jwt_handler import create_access_token
from src.services.auth.refresh_token_handler import verify_refresh_token, hash_token
from src.models.accounts import Account

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/refresh")
def refresh_access_token(
    refresh_token: str = Header(..., alias="X-Refresh-Token"),
    db: Session = Depends(get_db)
):
    hashed = hash_token(refresh_token)
    account = db.query(Account).filter(Account.refresh_token == hashed).first()

    if not account:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # ✅ 새 access_token 발급
    new_token = create_access_token(data={"sub": str(account.account_id)})

    return {"access_token": new_token}