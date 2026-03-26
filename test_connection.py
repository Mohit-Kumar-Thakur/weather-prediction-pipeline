# test_connection.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL"))

try:
    with engine.connect() as conn:
        print("PostgreSQL connected successfully!")
except Exception as e:
    print(f"Connection failed: {e}")