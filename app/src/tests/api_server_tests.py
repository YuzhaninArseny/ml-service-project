import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
import json
from ..config import PROMPT_PRICE, get_connection_params


def test_register_user(context_user):
    mock_db = MagicMock()
    mock_db.register.return_value = True
    user_data = {"username": "test_user_2", "password": "test_password"}
    response = context_user["client"].post("/register", json=user_data)
    assert response.status_code == 200
    assert response.json() == {"message": "User successfully registered!"} or response.json() == {"message": "User already registered!"}


def test_login_user(context_user):
    assert context_user["token"] is not None


def test_deposit(context_user):
    mock_db = MagicMock()
    mock_db.change_balance.return_value = None
    transaction_data = {"amount": 52}
    response = context_user["client"].post("/deposit", json=transaction_data, cookies={"access_token": context_user["token"]})
    assert response.status_code == 200
    assert response.json() == {"msg": "Transaction successfully deposited"}


def test_get_balance(context_user):
    mock_db = MagicMock()
    mock_db.get_balance.return_value = 52
    response = context_user["client"].get("/balance", cookies={"access_token": context_user["token"]})
    assert response.status_code == 200
    assert isinstance(response.json(), float)


def test_get_all_users(context_admin):
    mock_db = MagicMock()
    mock_db.get_all_users.return_value = [{}]
    response = context_admin["client"].get("/all_users", cookies={"access_token": context_admin["token"]})
    assert response.status_code == 200
    assert isinstance(json.loads(response.json()), list)


def test_get_user_transactions(context_user):
    mock_db = MagicMock()
    mock_db.get_user_transactions.return_value = [{}]
    response = context_user["client"].get("/all_transactions", cookies={"access_token": context_user["token"]})
    assert response.status_code == 200
    assert isinstance(json.loads(response.json()), list)


def test_get_anecdote(context_user):
    mock_db = MagicMock()
    mock_db.get_balance.return_value = PROMPT_PRICE + 100
    mock_db.change_balance.return_value = None
    mock_db.get_prediction_by_id.return_value = {"prediction": "the best joke"}

    # Сначала пополняем баланс, чтобы хватило на запрос
    context_user["client"].post("/deposit", json={"amount": 52},
                cookies={"access_token": context_user["token"]})

    response = context_user["client"].post("/anecdote", json={"prompt": "tell me joke"},
                           cookies={"access_token": context_user["token"]})

    assert response.status_code == 200
    assert "task_id" in response.json()

    task_id = response.json()["task_id"]
    response = context_user["client"].get(f"/anecdote/{task_id}", cookies={"access_token": context_user["token"]})
    assert response.status_code == 200
    assert "prediction" in response.json()
