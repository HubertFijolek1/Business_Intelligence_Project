"""
This module handles the creation of a SQLAlchemy engine from environment variables.
Call get_engine() to get a connected engine.
"""
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

def get_engine():
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT')
    db_name = os.getenv('DB_NAME')

    if not all([db_user, db_password, db_host, db_port, db_name]):
        raise ValueError("Database environment variables are not set properly.")

    try:
        engine = create_engine(
            f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
        )
        return engine
    except Exception as e:
        raise ConnectionError("Failed to create database engine") from e
