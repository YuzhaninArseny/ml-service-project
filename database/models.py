from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    login = Column(String, unique=True)
    password = Column(String)
    balance = Column(Integer)
    is_admin = Column(Boolean)

