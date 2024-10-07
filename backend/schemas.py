from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    password: str
    interest_rate: float = Field(..., ge=0, le=1)  # Interest rate between 0 and 1 (0% to 100%)

class User(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    username: str
    password: str

class AccountCreate(BaseModel):
    user_id: int
    balance: float = 0.0
    interest_rate: float = 0.01

class Account(BaseModel):
    id: int
    user_id: int
    balance: float
    interest_rate: float
    last_interest_calculation: datetime

    class Config:
        orm_mode = True

class TransactionCreate(BaseModel):
    account_id: int
    amount: float
    transaction_type: str
    note: str = ""

class Transaction(BaseModel):
    id: int
    account_id: int
    amount: float
    transaction_type: str
    timestamp: datetime  # Change this to datetime
    note: str

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat()  # Convert datetime to ISO format string
        }

class InterestRateUpdate(BaseModel):
    interest_rate: float = Field(..., ge=0, le=1)