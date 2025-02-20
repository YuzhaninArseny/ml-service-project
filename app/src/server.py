from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Depends, Response, Request
from auth import create_access_token

from database.database import UserManager
from shemas.shemas import UserData, Transaction, PredictionCreate

from config import get_url, SECRET_KEY, ALGORITHM
from jose import jwt, JWTError

app = FastAPI()

def get_token(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Token not found")
    return token

def authenticate(token: str):
    try:
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    expire = payload["exp"]
    expire_time = datetime.fromtimestamp(int(expire), tz=timezone.utc)
    if (not expire) or (expire_time < datetime.now(timezone.utc)):
        raise HTTPException(status_code=401, detail='Token has expired')

    user_id = payload["sub"]
    if not user_id:
        raise HTTPException(status_code=401, detail="User not found")

def is_admin(token: str):
    payload = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
    return payload["is_admin"]

@app.post("/register")
def register_user(user: UserData):
    if UserManager.register(get_url(), user.username, user.password, user.is_admin):
        return {"message": "User successfully registered!"}
    raise HTTPException(status_code=400, detail="Username already registered")


@app.post("/login")
def login(response: Response, user_data: UserData):
    user_id, is_admin = UserManager.authorization(get_url(), user_data.username, user_data.password)
    if not user_id:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token({"sub": str(user_id), "is_admin": is_admin})
    response.set_cookie("access_token", access_token, httponly=True)

    return {"access_token": access_token, "refresh_token": None}


@app.post("/deposit")
def deposit(transaction: Transaction, token: str = Depends(get_token)):
    try:
        authenticate(token)
    except HTTPException as e:
        raise e

    if transaction.amount == 0:
        raise HTTPException(status_code=400, detail="You cannot conduct zero-sum transactions.")
    UserManager.change_balance(get_url(), transaction.username, transaction.amount)
    return {"msg": "Transaction successfully deposited"}


@app.get("/balance")
def get_balance(username: str, token: str = Depends(get_token)):
    try:
        authenticate(token)
    except HTTPException as e:
        raise e

    user_balance = UserManager.get_balance(get_url(), username)
    return user_balance


@app.post("/add-prediction")
def add_prediction(prediction: PredictionCreate, token: str = Depends(get_token)):
    try:
        authenticate(token)
    except HTTPException as e:
        raise e

    UserManager.add_prediction(get_url(), prediction.username, prediction.prediction_result)
    return {"msg": "Prediction successfully added"}


@app.get("/predictions")
def get_predictions(username: str, token: str = Depends(get_token)):
    try:
        authenticate(token)
    except HTTPException as e:
        raise e

    predictions = UserManager.get_user_predictions(get_url(), username)
    return predictions

@app.get("/all_users")
def get_all_users(token: str = Depends(get_token)):
    try:
        authenticate(token)
    except HTTPException as e:
        raise e

    if not is_admin(token):
        raise HTTPException(status_code=401, detail="User not admin")

    return UserManager.get_all_users(get_url())