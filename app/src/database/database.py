import json
from contextlib import contextmanager
from typing import Generator, Any

from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
import os
from datetime import datetime

from .models import Base, User, Transaction, Prediction
from shemas.enums import TransactionType

load_dotenv()

POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")


class Database:
    def __init__(self, db_url: str):
        self._engine = create_engine(db_url)
        self._Session = sessionmaker(
            autocommit=False, autoflush=False, bind=self._engine
        )
        Base.metadata.create_all(self._engine)

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        session = self._Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()


class UserManager(Database):
    @classmethod
    def try_register(
        cls, db_url, username: str, password: str, is_admin: bool = False
    ) -> str:
        user_manager = cls(db_url)
        with user_manager.session_scope() as session:
            if session.query(User).filter_by(username=username).first():
                return "user already registered"
            new_user = User(username=username, password=password, is_admin=is_admin)
            session.add(new_user)

        return "user successfully registered"

    @classmethod
    def authorization(cls, db_url: str, username: str, password_for_verification: str):
        user_manager = cls(db_url)
        with user_manager.session_scope() as session:
            user = session.query(User).filter_by(username=username).first()
            if user and user.verify_password(user.password, password_for_verification):
                return user.id, user.is_admin
            return None, None

    @classmethod
    def get_all_users(cls, db_url: str):
        user_manager = cls(db_url)
        with user_manager.session_scope() as session:
            users = session.query(User).all()
            users = json.dumps([user.to_dict() for user in users])
        return users

    @classmethod
    def get_balance(cls, db_url: str, username: str) -> Any:
        user_manager = cls(db_url)
        with user_manager.session_scope() as session:
            user = session.query(User).filter_by(username=username).first()
            if user:
                return user.balance
            return None

    @classmethod
    def change_balance(cls, db_url: str, username: str, amount: float) -> None:
        user_manager = cls(db_url)
        with user_manager.session_scope() as session:
            user = session.query(User).filter_by(username=username).first()
            if user:
                if user.balance + amount < 0:
                    raise ValueError("Cannot change balance")
                user.balance += amount
                transactions_type = (
                    TransactionType.REPLENISHMENT
                    if amount > 0
                    else TransactionType.WITHDRAW
                )
                new_transaction = Transaction(
                    username=username,
                    amount=amount,
                    transaction_type=transactions_type.value,
                )
                session.add(new_transaction)

    @classmethod
    def add_prediction(
        cls, db_url: str, task_id: str, username: str, prediction: str, amount: float
    ) -> None:
        user_manager = cls(db_url)
        with user_manager.session_scope() as session:
            user = session.query(User).filter_by(username=username).first()
            if user:
                users_prediction = Prediction(
                    task_id=task_id,
                    username=username,
                    prediction_result=prediction,
                    amount=amount,
                )
                session.add(users_prediction)

    @classmethod
    def get_user_transactions(cls, db_url: str, username: str):
        user_manager = cls(db_url)
        with user_manager.session_scope() as session:
            transactions = session.query(Transaction).filter_by(username=username).all()
            transactions = json.dumps(
                [transaction.to_dict() for transaction in transactions]
            )
        return transactions

    @classmethod
    def get_user_predictions(cls, db_url: str, username: str):
        user_manager = cls(db_url)
        with user_manager.session_scope() as session:
            predictions = (
                session.query(Prediction).filter(Prediction.username == username).all()
            )
            predictions = json.dumps(
                [prediction.to_dict() for prediction in predictions]
            )
        return predictions

    @classmethod
    def get_prediction_by_id(cls, db_url: str, prediction_id: str, username: str):
        user_manager = cls(db_url)
        with user_manager.session_scope() as session:
            prediction = (
                session.query(Prediction)
                .filter(
                    (Prediction.task_id == prediction_id)
                    & (Prediction.username == username)
                )
                .first()
            )
            if prediction:
                return prediction.prediction_result
