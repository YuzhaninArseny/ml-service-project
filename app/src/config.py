from dotenv import load_dotenv
import os
import pika

load_dotenv()

POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = os.getenv("JWT_ALGORITHM")
PROMPT_PRICE = float(os.getenv("PROMPT_PRICE"))
RABBITMQ_DEFAULT_USER = os.getenv("RABBITMQ_DEFAULT_USER")
RABBITMQ_DEFAULT_PASS = os.getenv("RABBITMQ_DEFAULT_PASS")


def get_connection_params():
    return pika.ConnectionParameters(
        host="rabbitmq",
        port=5672,
        virtual_host="/",
        credentials=pika.PlainCredentials(
            username=RABBITMQ_DEFAULT_USER, password=RABBITMQ_DEFAULT_PASS
        ),
        heartbeat=0,
    )


def get_auth_data():
    return {"secret_key": SECRET_KEY, "algorithm": ALGORITHM}


def get_url():
    return f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@postgres:5432/{POSTGRES_DB}"
