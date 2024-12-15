import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()

db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')

def load_sales_data(engine):
    query = "SELECT * FROM sales"
    return pd.read_sql(query, engine)


def load_customer_data(engine):
    query = "SELECT * FROM customers"
    return pd.read_sql(query, engine)


def load_product_data(engine):
    query = "SELECT * FROM products"
    return pd.read_sql(query, engine)


def load_marketing_data(engine):
    query = "SELECT * FROM marketing"
    return pd.read_sql(query, engine)

if __name__ == "__main__":
    try:
        engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        exit(1)
    sales = load_sales_data(engine)
    customers = load_customer_data(engine)
    products = load_product_data(engine)
    marketing = load_marketing_data(engine)

    sales.to_csv('data/raw/sales.csv', index=False)
    customers.to_csv('data/raw/customers.csv', index=False)
    products.to_csv('data/raw/products.csv', index=False)
    marketing.to_csv('data/raw/marketing.csv', index=False)

    print("Data loaded successfully.")
