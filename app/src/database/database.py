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
        # Base.metadata.drop_all(self._engine)
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
                    task_id=task_id, username=username, prediction_result=prediction, amount=amount
                )
                session.add(users_prediction)

    @classmethod
    def get_user_transactions(cls, db_url: str, username: str):
        """Получает все транзакции для указанного пользователя."""
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
        with (user_manager.session_scope() as session):
            prediction = session.query(Prediction).filter((Prediction.task_id==prediction_id) & (Prediction.username==username)).first()
            if prediction:
                return prediction.prediction_result

if __name__ == "__main__":
    db_url = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@localhost:5432/{POSTGRES_DB}"
    print(db_url)
    # UserManager.register(db_url, "demo_user", "a")
    UserManager.try_register(db_url, "demo_admin", "adminpassword", is_admin=True)
    #
    # is_authorized = UserManager.authorization(db_url, "demo_user", "a")
    # print("Authorization successful:", is_authorized)
    #
    balance = UserManager.get_balance(db_url, "demo_admin")
    print("Balance:", balance)

    # UserManager.change_balance(db_url, "demo_admin", 50.0, datetime.utcnow())
    # new_balance = UserManager.get_balance(db_url, "demo_admin")
    # print("New Balance:", new_balance)
    # UserManager.change_balance(db_url, "demo_user", -25.0, datetime.utcnow)
    # new_balance = UserManager.get_balance(db_url, "demo_user")
    # print("New Balance:", new_balance)

    # transactions = UserManager.get_user_transactions(db_url, "demo_admin")
    # print("Transactions:", transactions)
    #
    # UserManager.add_prediction(db_url, "qwsdqfcQE-33434-34254", "demo_admin", "hahahahahahhahhaahha", -80)

    # UserManager.register(db_url, "testman", "password")
    # date = datetime.utcnow()
    # UserManager.change_balance(db_url, "testman", 50, date)
    # UserManager.add_prediction(db_url, "testman", "bla-bla-bla", date)
    # UserManager.change_balance(db_url, "testman", -50, date)
    # UserManager.add_prediction(db_url, "testman", "fwegvfawgvawrv", date)
    # UserManager.change_balance(db_url, "testman", 50, date)
    # UserManager.add_prediction(db_url, "testman", "qwertyuiop[", date)
    #
    #
    # predictions = UserManager.get_user_predictions(db_url, "demo_admin")
    # print("Predictions:", predictions)
    # prediction_by_id = UserManager.get_prediction_by_id(db_url, "qwsdqfcQE-33434-34254", "demo_admin")

    # delete DB
    # db = Database(db_url)
