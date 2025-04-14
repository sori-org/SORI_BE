from pydantic import BaseModel


class AccountBase(BaseModel):
    kakao_id: int


class AccountCreate(AccountBase):
    pass


class AccountOut(AccountBase):
    account_id: int

    class Config:
        orm_mode = True