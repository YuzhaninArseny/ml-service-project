import streamlit as st
import requests
from jose import jwt, JWTError
import json
from config import SECRET_KEY, ALGORITHM, BASE_URL
import time


# Функция для регистрации пользователя
def register_user(username, password, is_admin):
    url = f"{BASE_URL}/register"
    response = requests.post(
        url, json={"username": username, "password": password, "is_admin": is_admin}
    )
    return response.json()


# Функция для входа пользователя
def login_user(username, password):
    url = f"{BASE_URL}/login"
    response = requests.post(url, json={"username": username, "password": password})
    return response.json()


def get_all_users():
    url = f"{BASE_URL}/all_users"
    response = requests.get(url)
    return response.json()


def is_admin(token: str):
    try:
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
        return payload["is_admin"]
    except JWTError:
        return False


if "token" not in st.session_state:
    st.session_state.token = None
if "show_register" not in st.session_state:
    st.session_state.show_register = True
if "show_login" not in st.session_state:
    st.session_state.show_login = True

# Кнопки для регистрации и входа
if st.session_state.show_register and st.session_state.show_login:
    tab1, tab2 = st.tabs(["Register", "Login"])

    with tab1:
        if st.session_state.get("show_register", True):
            st.title("Registration")
            with st.form("Register"):
                username = st.text_input("Username", key="register_username")
                password = st.text_input(
                    "Password", type="password", key="register_password"
                )
                is_admin_flag = st.checkbox("Is Admin", key="register_is_admin")
                if st.form_submit_button("Register"):
                    answer = register_user(username, password, is_admin_flag)
                    if answer.get("msg", False):
                        st.success(answer["msg"])
                        st.session_state.show_register = False
                    else:
                        st.error(answer["detail"])

    with tab2:
        if st.session_state.get("show_login", True):
            st.title("Login")
            with st.form("Login"):
                login_username = st.text_input("Username", key="login_username")
                login_password = st.text_input(
                    "Password", type="password", key="login_password"
                )
                if st.form_submit_button("Login"):
                    result = login_user(login_username, login_password)
                    if "access_token" in result:
                        st.session_state.token = result["access_token"]
                        st.session_state.show_register = False
                        st.session_state.show_login = False
                        st.success("Logged in successfully!")
                        st.rerun()
                    else:
                        st.error("Login failed!")

# Проверка состояния авторизации
if (
    st.session_state.token
    and not st.session_state.show_login
    and not st.session_state.show_register
):
    with st.sidebar:
        if st.button("Logout", key="logout_button"):
            st.session_state.show_login = True
            st.session_state.show_register = True
            st.rerun()

    if st.button("Get Balance", key="get_balance_button"):
        url = f"{BASE_URL}/balance"
        response = requests.get(url, cookies={"access_token": st.session_state.token})
        st.write(response.json())

    # Вкладка для депозита
    with st.container(border=True):
        amount = st.number_input("Amount", key="deposit_amount")
        if st.button("Top up balance", key="deposit_button"):
            url = f"{BASE_URL}/deposit"
            response = requests.post(
                url,
                json={"amount": amount},
                cookies={"access_token": st.session_state.token},
            )
            answer = response.json()
            if answer.get("msg", False):
                st.success(answer["msg"])
            else:
                st.error(response.json()["detail"])

    # Вкладка для получения предсказаний
    if st.button("Get Predictions", key="get_predictions_button"):
        url = f"{BASE_URL}/predictions"
        response = requests.get(url, cookies={"access_token": st.session_state.token})
        predictions = json.loads(response.json())
        if predictions:
            st.dataframe(predictions)
        else:
            st.info("No predictions available!")

    # Вкладка для получения анекдота
    with st.container(border=True):
        prompt = st.text_input("Запрос", key="anecdote_prompt")
        if st.button("Get Anecdote", key="get_anecdote_button"):
            url = f"{BASE_URL}/anecdote"
            response = requests.post(
                url,
                json={"prompt": prompt},
                cookies={"access_token": st.session_state.token},
            )
            if response.status_code != 200:
                content = response.content.decode("utf-8")
                content = json.loads(content)
                st.error(content["detail"])
            else:
                # st.write(response.json()["prediction"])
                task_id = response.json().get("task_id")
                if task_id:
                    with st.spinner("Processing the prompt..."):
                        while True:
                            url = f"{BASE_URL}/anecdote/{task_id}"
                            response = requests.get(url, cookies={"access_token": st.session_state.token})
                            answer = response.json()
                            if answer is not None and answer.get("prediction", False):
                                st.success("Result received!")
                                st.write(answer["prediction"])
                                break
                            elif "detail" in answer and answer["detail"] == "Task result not found":
                                time.sleep(5)
                            else:
                                st.error("An error occurred while retrieving the result.")
                                break
                else:
                    st.error("Failed to send request!")

    if is_admin(st.session_state.token):
        if st.button("Get all users", key="get_all_users_button"):
            url = f"{BASE_URL}/all_users"
            response = requests.get(
                url, cookies={"access_token": st.session_state.token}
            )
            predictions = json.loads(response.json())
            if predictions:
                st.dataframe(predictions)
            else:
                st.error("No information about all users")
