from dotenv import load_dotenv
import os
import pika

load_dotenv()

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
