import hashlib
from datetime import datetime
from typing import Any

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)
    balance = Column(Integer)
    is_admin = Column(Boolean)

    transactions = relationship("Transaction", back_populates="user")
    predictions = relationship("Prediction", back_populates="user")

    def __init__(
        self,
        username: str,
        password: str,
        balance: float = 0.0,
        is_admin: bool = False,
        *args: Any,
        **kwargs: Any
    ):
        super().__init__(*args, **kwargs)
        self.username = username
        self.password = self._hash_password(password)
        self.balance = balance
        self.is_admin = is_admin

    @staticmethod
    def _hash_password(password: str):
        hash = hashlib.sha256(password.encode()).hexdigest()
        return hash

    @staticmethod
    def verify_password(stored_password_hash: str, password: str) -> bool:
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        return stored_password_hash == hashed_password


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    transaction_type = Column(
        String, nullable=False
    )  # Например, 'replenishment' или 'withdraw'
    date = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="transactions")


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    prediction_result = Column(
        String, nullable=False
    )  # Буду анекдоты пользователю генерировать, поэтому string
    date = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="predictions")
