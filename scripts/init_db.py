import os
import time
import psycopg2
from app import create_app, db

def wait_for_db():
    max_tries = 30
    while max_tries > 0:
        try:
            conn = psycopg2.connect(
                host=os.getenv('DB_HOST'),
                database=os.getenv('DB_DATABASE'),
                user=os.getenv('DB_USERNAME'),
                password=os.getenv('DB_PASSWORD'),
                port=os.getenv('DB_PORT', 5432)
            )
            conn.close()
            print("Successfully connected to database")
            return True
        except psycopg2.OperationalError:
            print(f"Waiting for database... {max_tries} tries left")
            max_tries -= 1
            time.sleep(1)
    return False

def init_db():
    if not wait_for_db():
        print("Could not connect to database")
        return

    app = create_app()
    with app.app_context():
        db.create_all()
        print("Database tables created")

if __name__ == "__main__":
    init_db() 