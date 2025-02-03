from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from ..user import User

class Database:
    def __init__(self, db_url: str):
        self._engine = create_engine(db_url)
        self._Session = sessionmaker(autocommit=False, autoflush=False, bind=self._engine)

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
    def register(cls, user: User) -> None:
        pass

    @classmethod
    def authorization(cls, user: User) -> None:
        pass

    @classmethod
    def get_balance(cls, user: User) -> float:
        pass

    @classmethod
    def change_balance(cls, user: User, new_balance: int) -> None:
        pass
