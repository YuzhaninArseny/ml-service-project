from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    login = Column(String, unique=True)
    password = Column(String)
    balance = Column(Integer)
    is_admin = Column(Boolean)

    transactions = relationship('Transaction', back_populates='user')
    predictions = relationship('Prediction', back_populates='user')

class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String, nullable=False)  # Например, 'replenishment' или 'withdraw'
    date = Column(DateTime, default=datetime.utcnow)

    user = relationship('User', back_populates='transactions')

class Prediction(Base):
    __tablename__ = 'predictions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    prediction_result = Column(String, nullable=False) # Буду анекдоты пользователю генерировать, поэтому string
    date = Column(DateTime, default=datetime.utcnow)

    user = relationship('User', back_populates='predictions')