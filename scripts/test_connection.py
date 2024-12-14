import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

def load_environment_variables():
    load_dotenv()
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT')
    db_name = os.getenv('DB_NAME')
    return db_user, db_password, db_host, db_port, db_name

def main():
    db_user, db_password, db_host, db_port, db_name = load_environment_variables()
    try:
        engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')
        df = pd.read_sql("SELECT 1", engine)
        print("Connection Successful:", df)
    except Exception as e:
        print("Connection Failed:", e)

if __name__ == "__main__":
    main()