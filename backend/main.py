from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List

import models, schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/signup", response_model=schemas.User)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login", response_model=schemas.User)
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if not db_user or db_user.password != user.password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return db_user

@app.get("/account/{user_id}", response_model=schemas.Account)
def get_account(user_id: int, db: Session = Depends(get_db)):
    account = db.query(models.Account).filter(models.Account.user_id == user_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account

@app.post("/transaction", response_model=schemas.Transaction)
def create_transaction(transaction: schemas.TransactionCreate, db: Session = Depends(get_db)):
    db_transaction = models.Transaction(**transaction.dict())
    db.add(db_transaction)
    account = db.query(models.Account).filter(models.Account.id == transaction.account_id).first()
    account.balance += transaction.amount
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

@app.get("/transactions/{account_id}", response_model=List[schemas.Transaction])
def get_transactions(account_id: int, db: Session = Depends(get_db)):
    transactions = db.query(models.Transaction).filter(models.Transaction.account_id == account_id).all()
    return transactions

@app.post("/apply-interest")
def apply_interest(db: Session = Depends(get_db)):
    accounts = db.query(models.Account).all()
    for account in accounts:
        interest = account.balance * (account.interest_rate / 365)
        account.balance += interest
        transaction = models.Transaction(
            account_id=account.id,
            amount=interest,
            transaction_type="interest",
            note="Daily interest"
        )
        db.add(transaction)
    db.commit()
    return {"message": "Interest applied successfully"}