from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UserData(BaseModel):
    username: str
    password: str
    is_admin: Optional[bool] = False


class Transaction(BaseModel):
    amount: float


class PredictionCreate(BaseModel):
    prediction_result: str


class PredictionResponse(BaseModel):
    id: int
    prediction_result: str
    date: datetime


class AnecdoteRequest(BaseModel):
    prompt: str
