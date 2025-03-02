from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = os.getenv("JWT_ALGORITHM")

# Базовый URL вашего FastAPI приложения
BASE_URL = "http://localhost:8080"
