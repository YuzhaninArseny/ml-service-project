import hashlib
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Base
from models import User, Transaction, Prediction
from dotenv import load_dotenv
import os

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
    def __init__(self, db_url: str):
        super().__init__(db_url)

    @classmethod
    def register(cls, db_url, username: str, password: str, is_admin: bool = False) -> None:
        user_manager = cls(db_url)
        with user_manager.session_scope() as session:
            if session.query(User).filter_by(username=username).first():
                print(f"User with username '{username}' already exists.")
                return

            new_user = User(username=username, password=cls._hash_password(password), is_admin=is_admin)
            session.add(new_user)

    @classmethod
    def authorization(
        cls, db_url: str, username: str, password_for_verification: str
    ) -> bool:
        user_manager = cls(db_url)
        with user_manager.session_scope() as session:
            user = session.query(User).filter_by(username=username).first()
            print(user)
            if user and user.verify_password(user.password, password_for_verification):
                return True
            return False

    @classmethod
    def get_balance(
            cls, db_url: str, username: str
    ) -> float:
        user_manager = cls(db_url)
        with user_manager.session_scope() as session:
            user = session.query(User).filter_by(username=username).first()
            if user:
                return user.balance
            return 0.0

    @classmethod
    def change_balance(cls, db_url: str, username: str, amount: float) -> None:
        user_manager = cls(db_url)
        with user_manager.session_scope() as session:
            user = session.query(User).filter_by(username=username).first()
            if user:
                user.balance += amount

    @classmethod
    def get_user_transactions(cls, db_url: str, user_id: int):
        """Получает все транзакции для указанного пользователя."""
        user_manager = cls(db_url)
        with user_manager.session_scope() as session:
            transactions = session.query(Transaction).filter_by(user_id=user_id).all()
        return transactions

    @classmethod
    def get_user_predictions(cls, db_url: str, user_id: int):
        """Получает все транзакции для указанного пользователя."""
        user_manager = cls(db_url)
        with user_manager.session_scope() as session:
            predictions = session.query(Prediction).filter_by(user_id=user_id).all()
        return predictions

if __name__ == "__main__":
    db_url = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@127.0.0.1:5432/{POSTGRES_DB}"
    UserManager.register(db_url, "demo_user", "a")
    UserManager.register(db_url, "demo_admin", "adminpassword", is_admin=True)

    is_authorized = UserManager.authorization(db_url, "demo_user", "a")
    print("Authorization successful:", is_authorized)

    balance = UserManager.get_balance(db_url, "demo_user")
    print("Balance:", balance)

    UserManager.change_balance(db_url, "demo_user", 50.0)
    new_balance = UserManager.get_balance(db_url, "demo_user")
    print("New Balance:", new_balance)
    UserManager.change_balance(db_url, "demo_user", -25.0)
    new_balance = UserManager.get_balance(db_url, "demo_user")
    print("New Balance:", new_balance)

    transactions = UserManager.get_user_transactions(db_url, 1)
    print("Transactions:", transactions)

    predictions = UserManager.get_user_predictions(db_url, 1)
    print("Predictions:", predictions)