import os
from fastapi import FastAPI, Depends, HTTPException, StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timezone, timedelta
from typing import List
import logging

import models, schemas
from database import SessionLocal, engine

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the static files
app.mount("/", StaticFiles(directory="frontend/build", html=True), name="static")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/check_username/{username}")
def check_username(username: str, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    return {"message": "Username is available"}

@app.post("/signup", response_model=schemas.User)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    new_user = models.User(username=user.username, password=user.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create an account for the new user with the specified interest rate
    new_account = models.Account(user_id=new_user.id, balance=0.0, interest_rate=user.interest_rate)
    db.add(new_account)
    db.commit()
    
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
    apply_interest(account, db)
    return account

@app.post("/transaction", response_model=schemas.Transaction)
def create_transaction(transaction: schemas.TransactionCreate, db: Session = Depends(get_db)):
    db_transaction = models.Transaction(**transaction.dict())
    db.add(db_transaction)
    account = db.query(models.Account).filter(models.Account.id == transaction.account_id).first()
    apply_interest(account, db)  # Apply interest before updating balance
    account.balance += transaction.amount
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

@app.get("/transactions/{account_id}", response_model=List[schemas.Transaction])
def get_transactions(account_id: int, db: Session = Depends(get_db)):
    try:
        logger.info(f"Fetching transactions for account_id: {account_id}")
        account = db.query(models.Account).filter(models.Account.id == account_id).first()
        if not account:
            logger.warning(f"Account not found for account_id: {account_id}")
            raise HTTPException(status_code=404, detail="Account not found")
        
        apply_interest(account, db)  # Apply interest before fetching transactions
        
        transactions = db.query(models.Transaction).filter(models.Transaction.account_id == account_id).all()
        logger.info(f"Found {len(transactions)} transactions for account_id: {account_id}")
        
        # Convert datetime to string if necessary
        for transaction in transactions:
            if isinstance(transaction.timestamp, datetime):
                transaction.timestamp = transaction.timestamp.isoformat()
        
        return transactions
    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching transactions for account_id {account_id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error while fetching transactions for account_id {account_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@app.put("/account/{user_id}/interest_rate")
def update_interest_rate(user_id: int, interest_rate: schemas.InterestRateUpdate, db: Session = Depends(get_db)):
    account = db.query(models.Account).filter(models.Account.user_id == user_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    apply_interest(account, db)  # Apply interest before updating rate
    account.interest_rate = interest_rate.interest_rate
    db.commit()
    return {"message": "Interest rate updated successfully"}

def apply_interest(account: models.Account, db: Session):
    current_time = datetime.now(timezone.utc)
    
    # Ensure last_interest_calculation is offset-aware
    if account.last_interest_calculation.tzinfo is None:
        account.last_interest_calculation = account.last_interest_calculation.replace(tzinfo=timezone.utc)
    
    days_since_last_calculation = (current_time - account.last_interest_calculation).days
    
    if days_since_last_calculation > 0:
        for day in range(days_since_last_calculation):
            interest_date = account.last_interest_calculation + timedelta(days=day+1)
            daily_interest = account.balance * (account.interest_rate / 365)
            account.balance += daily_interest
            
            # Create a transaction for the daily interest
            transaction = models.Transaction(
                account_id=account.id,
                amount=daily_interest,
                transaction_type="interest",
                timestamp=interest_date,
                note=f"Daily interest for {interest_date.date()}"
            )
            db.add(transaction)
        
        account.last_interest_calculation = current_time
        db.commit()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)