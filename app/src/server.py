import json
import uuid
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Depends, Response, Request
from auth import create_access_token

from database.database import UserManager
from shemas.shemas import UserData, Transaction, PredictionCreate, AnecdoteRequest

from config import get_url, SECRET_KEY, ALGORITHM
from jose import jwt, JWTError
import pika
from ml_service.config import get_connection_params

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
    print(get_url())
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

task_results = {}

@app.post("/anecdote")
def get_anecdote(prompt_data: AnecdoteRequest, token: str = Depends(get_token)):
    try:
        authenticate(token)
    except HTTPException as e:
        raise e

    with pika.BlockingConnection(get_connection_params()) as connection:
        with connection.channel() as channel:
            channel.queue_declare(queue="ml_task_queue", durable=True)
            channel.queue_declare(queue="result_ml_task_queue", durable=True)

            task_id = str(uuid.uuid4())
            task = {
                "id": task_id,
                "prompt": prompt_data.prompt,
            }

            channel.basic_publish(
                exchange="",
                routing_key="ml_task_queue",
                body=json.dumps(task),
                properties=pika.BasicProperties(
                    delivery_mode=2
                )
            )

            def on_response(ch, method, properties, body):
                answer = json.loads(body)
                if answer["id"] == task_id:
                    task_results[answer["id"]] = answer["prediction"]
                    channel.basic_ack(delivery_tag=method.delivery_tag)

            channel.basic_consume(
                queue="result_ml_task_queue",
                on_message_callback=on_response,
            )

            while task_id not in task_results:
                connection.process_data_events()

            result = task_results.pop(task_id)
            UserManager.add_prediction(get_url(), prompt_data.username, result)

    return {"prediction": result}

