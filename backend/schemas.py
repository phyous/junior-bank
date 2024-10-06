from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    name: str

class UserCreate(UserBase):
    password: str
    initial_balance: float
    interest_rate: float

class User(UserBase):
    id: int

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    username: str
    password: str

class AccountBase(BaseModel):
    balance: float
    interest_rate: float

class Account(AccountBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True

class TransactionBase(BaseModel):
    amount: float
    transaction_type: str
    note: Optional[str] = None

class TransactionCreate(TransactionBase):
    account_id: int

class Transaction(TransactionBase):
    id: int
    account_id: int
    timestamp: datetime

    class Config:
        orm_mode = True