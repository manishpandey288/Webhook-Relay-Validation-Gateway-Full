from sqlalchemy import create_engine
from config import settings
import sys

def check_db():
    print(f"Connecting to {settings.DATABASE_URL}")
    try:
        engine = create_engine(settings.DATABASE_URL)
        connection = engine.connect()
        print("Successfully connected to the database!")
        connection.close()
    except Exception as e:
        print(f"Failed to connect to the database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    check_db()
