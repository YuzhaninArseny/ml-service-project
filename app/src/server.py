import json
import uuid
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Depends, Response, Request
from auth import create_access_token

from database.database import UserManager
from shemas.shemas import UserData, Transaction, PredictionCreate, AnecdoteRequest

from config import get_url, SECRET_KEY, ALGORITHM, PROMPT_PRICE
from jose import jwt, JWTError
import pika
from ml_service.config import get_connection_params

app = FastAPI()


def get_token(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Token not found")
    return token


def authenticate(request: Request):
    token = get_token(request)
    try:
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    expire = payload["exp"]
    expire_time = datetime.fromtimestamp(int(expire), tz=timezone.utc)
    if (not expire) or (expire_time < datetime.now(timezone.utc)):
        raise HTTPException(status_code=401, detail="Token has expired")

    user_id = payload["sub"]
    if not user_id:
        raise HTTPException(status_code=401, detail="User not found")

    return token


def is_admin(token: str):
    payload = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
    return payload["is_admin"]


def get_username_from_token(token: str):
    payload = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
    return payload["username"]


@app.post("/register")
def register_user(user: UserData):
    if UserManager.register(get_url(), user.username, user.password, user.is_admin):
        return {"message": "User successfully registered!"}
    raise HTTPException(status_code=400, detail="Username already registered")


@app.post("/login")
def login(response: Response, user_data: UserData):
    user_id, is_admin = UserManager.authorization(
        get_url(), user_data.username, user_data.password
    )
    if not user_id:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token(
        {"sub": str(user_id), "username": user_data.username, "is_admin": is_admin}
    )
    response.set_cookie("access_token", access_token, httponly=True)

    return {"access_token": access_token, "refresh_token": None}


@app.post("/deposit")
def deposit(transaction: Transaction, token: str = Depends(authenticate)):
    if transaction.amount == 0:
        raise HTTPException(
            status_code=400, detail="You cannot conduct zero-sum transactions."
        )
    try:
        UserManager.change_balance(
            get_url(), get_username_from_token(token), transaction.amount
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"msg": "Transaction successfully deposited"}


@app.get("/balance")
def get_balance(token: str = Depends(authenticate)):
    user_balance = UserManager.get_balance(get_url(), get_username_from_token(token))
    return user_balance


@app.get("/predictions")
def get_predictions(token: str = Depends(authenticate)):
    predictions = UserManager.get_user_predictions(
        get_url(), get_username_from_token(token)
    )
    return predictions


@app.get("/all_users")
def get_all_users(token: str = Depends(authenticate)):
    if not is_admin(token):
        raise HTTPException(status_code=400, detail="User not admin")

    return UserManager.get_all_users(get_url())

@app.get("/all_transactions")
def get_user_transactions(token: str = Depends(authenticate)):
    username = get_username_from_token(token)
    transactions = UserManager.get_user_transactions(get_url(), username)
    return transactions



@app.post("/anecdote")
def get_anecdote(prompt_data: AnecdoteRequest, token: str = Depends(authenticate)):
    username = get_username_from_token(token)

    if (
        UserManager.get_balance(get_url(), username)
        < PROMPT_PRICE
    ):
        raise HTTPException(status_code=400, detail="Insufficient funds")

    with pika.BlockingConnection(get_connection_params()) as connection:
        with connection.channel() as channel:
            channel.queue_declare(queue="ml_task_queue", durable=True)

            task_id = str(uuid.uuid4())
            task = {
                "id": task_id,
                "prompt": prompt_data.prompt,
                "username": username,
                "amount": -PROMPT_PRICE,
            }

            channel.basic_publish(
                exchange="",
                routing_key="ml_task_queue",
                body=json.dumps(task),
                properties=pika.BasicProperties(delivery_mode=2),
            )

            UserManager.change_balance(get_url(), username, -PROMPT_PRICE)

    return {"task_id": task_id}


@app.get("/anecdote/{task_id}")
def get_anecdote_result(task_id: str, token: str = Depends(authenticate)):
    username = get_username_from_token(token)
    predictions = UserManager.get_prediction_by_id(get_url(), task_id, username)
    if predictions is None:
        raise HTTPException(status_code=400, detail="Task result not found")
    return {"prediction": predictions}