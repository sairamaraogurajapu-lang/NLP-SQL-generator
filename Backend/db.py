import psycopg2
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

def get_connection():
    return psycopg2.connect(
        host="127.0.0.1",
        database=os.getenv("DB_NAME", "employees_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "Hanumansingh123"),
        port=os.getenv("DB_PORT", "5432")
    )
