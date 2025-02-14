from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
import os

from database.database import UserManager
from shemas.shemas import UserCreate, UserLogin, Transaction, PredictionCreate, PredictionResponse

load_dotenv()

POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

db_url = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@postgres:5432/{POSTGRES_DB}"

app = FastAPI()

@app.post("/register")
def register_user(user: UserCreate):
    if UserManager.register(db_url, user.username, user.password, user.is_admin):
        return {"message": "User successfully registered!"}
    raise HTTPException(status_code=400, detail="Username already registered")

@app.post("/login")
def login(user: UserLogin):
    if UserManager.authorization(db_url, user.username, user.password_for_verification):
        return {"msg": "Login successful"}
    raise HTTPException(status_code=400, detail="Invalid credentials")

@app.post("/deposit")
def deposit(transaction: Transaction):
    if transaction.amount == 0:
        raise HTTPException(status_code=400, detail="You cannot conduct zero-sum transactions.")
    UserManager.change_balance(db_url, transaction.username, transaction.amount)
    return {"msg": "Transaction successfully deposited"}

@app.get("/balance")
def get_balance(username: str):
    user_balance = UserManager.get_balance(db_url, username)
    return user_balance

@app.post("/add-prediction")
def add_prediction(prediction: PredictionCreate):
    UserManager.add_prediction(db_url, prediction.username, prediction.prediction_result)
    return {"msg": "Prediction successfully added"}

@app.get("/predictions")
def get_predictions(username: str):
    predictions = UserManager.get_user_predictions(db_url, username)
    return predictions