from datetime import datetime
from typing import Optional

from pydantic import BaseModel

class UserData(BaseModel):
    username: str
    password: str
    is_admin: Optional[bool] = False

class Transaction(BaseModel):
    username: str
    amount: float

class PredictionCreate(BaseModel):
    username: str
    prediction_result: str

class PredictionResponse(BaseModel):
    id: int
    prediction_result: str
    date: datetime

class AnecdoteRequest(BaseModel):
    username: str
    prompt: str