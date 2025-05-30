from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.models.users import User
from src.models.accounts import Account
from src.services.auth.kakao_unlink import unlink_kakao_user

def get_or_create_kakao_user(db: Session, kakao_user_data: dict, access_token: str):
    kakao_id = kakao_user_data["kakao_id"]

    # 1. accounts 테이블에서 kakao_id로 검색
    account = db.query(Account).filter_by(kakao_id=kakao_id).first()

    if account:
        # 유저도 찾기
        user = db.query(User).filter_by(account_id=account.account_id).first()
        return user, False  # 이미 가입된 유저

    # 2. 신규 계정 생성
    try:
        new_account = Account(kakao_id=kakao_id)
        db.add(new_account)
        db.flush()  # account_id 확보

        new_user = User(
            account_id=new_account.account_id,
            display_name=kakao_user_data.get("nickname", "사용자"),
            profile_image=kakao_user_data.get("profile_image")
        )
        db.add(new_user)
        db.commit()
        return new_user, True

    except Exception as e:
        db.rollback()
        try:
            unlink_kakao_user(access_token)
        except Exception as unlink_error:
            print("⚠️ 언링크 실패:", unlink_error)

        raise HTTPException(status_code=500, detail="사용자 등록 실패 - 카카오 연동 해제됨")