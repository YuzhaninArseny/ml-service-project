import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from ..config import get_url
from ..server import app
from ..database.models import Base
import re

client = TestClient(app)

@pytest.fixture
def db_url():
    test_db_url = f"postgresql+psycopg2://test_user:password@localhost:5433/test-db"
    return test_db_url

@pytest.fixture
def init_db(db_url):
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

@pytest.fixture(name="context_user")
def auth_user():
    user_data = {"username": "test_user", "password": "test_password"}
    client.post("/register", json=user_data)
    response = client.post("/login", json=user_data)

    token = response.json()["access_token"]
    return {"client": client, "token": token}

@pytest.fixture(name="context_admin")
def auth_admin():
    admin_user_data = {"username": "test_admin", "password": "test_password", "is_admin": True}
    client.post("/register", json=admin_user_data)
    response = client.post("login", json=admin_user_data)

    token = response.json()["access_token"]
    return {"client": client, "token": token}

