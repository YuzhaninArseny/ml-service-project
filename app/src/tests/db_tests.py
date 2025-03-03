import pytest
from ..database.database import UserManager
from unittest.mock import MagicMock, patch
import json


def test_try_register(init_db, db_url):
    result = UserManager.try_register(db_url, "test_user", "password")
    assert result == "user successfully registered"

    result = UserManager.try_register(db_url, "test_user", "password")
    assert result == "user already registered"

def test_authorization(init_db, db_url):
    UserManager.try_register(db_url, "test_user", "password")

    user_id, is_admin = UserManager.authorization(db_url, "test_user", "password")
    assert user_id is not None
    assert is_admin is False

    user_id, is_admin = UserManager.authorization(db_url, "test_user", "wrong_password")
    assert user_id is None
    assert is_admin is None

    user_id, is_admin = UserManager.authorization(db_url, "non_existent_user", "password")
    assert user_id is None
    assert is_admin is None

def test_get_all_users(init_db, db_url):
    UserManager.try_register(db_url, "user1", "password1")
    UserManager.try_register(db_url, "user2", "password2")

    users = UserManager.get_all_users(db_url)
    assert len(json.loads(users)) == 2

def test_get_balance(init_db, db_url):
    UserManager.try_register(db_url, "test_user", "password")

    balance = UserManager.get_balance(db_url, "test_user")
    assert balance == 0

    balance = UserManager.get_balance(db_url, "non_existent_user")
    assert balance is None

def test_change_balance(init_db, db_url):
    UserManager.try_register(db_url, "test_user", "password")
    UserManager.change_balance(db_url, "test_user", 100)

    balance = UserManager.get_balance(db_url, "test_user")
    assert balance == 100

    UserManager.change_balance(db_url, "test_user", -50)
    balance = UserManager.get_balance(db_url, "test_user")
    assert balance == 50

    with pytest.raises(ValueError, match="Cannot change balance"):
        UserManager.change_balance(db_url, "test_user", -100)

def test_add_prediction(init_db, db_url):
    UserManager.try_register(db_url, "test_user", "password")
    UserManager.add_prediction(db_url, "task1", "test_user", "prediction1", -10)

    predictions = UserManager.get_user_predictions(db_url, "test_user")
    assert len(json.loads(predictions)) == 1

def test_get_user_transactions(init_db, db_url):
    UserManager.try_register(db_url, "test_user", "password")
    UserManager.change_balance(db_url, "test_user", 100)
    UserManager.change_balance(db_url, "test_user", -50)

    transactions = UserManager.get_user_transactions(db_url, "test_user")
    assert len(json.loads(transactions)) == 2

def test_get_user_predictions(init_db, db_url):
    UserManager.try_register(db_url, "test_user", "password")
    UserManager.add_prediction(db_url, "task1", "test_user", "prediction1", -10)
    UserManager.add_prediction(db_url, "task2", "test_user", "prediction2", -20)

    predictions = UserManager.get_user_predictions(db_url, "test_user")
    assert len(json.loads(predictions)) == 2

def test_get_prediction_by_id(init_db, db_url):
    UserManager.try_register(db_url, "test_user", "password")
    UserManager.add_prediction(db_url, "task1", "test_user", "prediction1", -10)

    prediction = UserManager.get_prediction_by_id(db_url, "task1", "test_user")
    assert prediction == "prediction1"

    prediction = UserManager.get_prediction_by_id(db_url, "non_existent_task", "test_user")
    assert prediction is None