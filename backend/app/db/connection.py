
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Find the project's root directory
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Load environment variables
load_dotenv(PROJECT_ROOT / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is missing from .env")

# Create database engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

def test_connection():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT current_database()"))
        print("Connected successfully!")
        print("Database:", result.scalar())

if __name__ == "__main__":
    test_connection()
