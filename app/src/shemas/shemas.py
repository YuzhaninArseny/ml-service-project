from datetime import datetime

from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str
    is_admin: bool = False

class UserLogin(BaseModel):
    username: str
    password_for_verification: str

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