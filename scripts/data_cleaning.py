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

engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')


def clean_sales_data(df):
    df.dropna(subset=['order_id', 'customer_id', 'product_id', 'quantity', 'total_price'], inplace=True)
    df['order_date'] = pd.to_datetime(df['order_date'])
    return df


def clean_customer_data(df):
    df.dropna(subset=['customer_id', 'signup_date', 'email'], inplace=True)
    df['signup_date'] = pd.to_datetime(df['signup_date'])
    return df


def clean_product_data(df):
    df.dropna(subset=['product_id', 'product_name', 'price'], inplace=True)
    return df


def clean_marketing_data(df):
    df.dropna(subset=['campaign_id', 'campaign_name', 'spend', 'conversions'], inplace=True)
    return df


def feature_engineering_sales(df):
    df['month'] = df['order_date'].dt.month
    df['year'] = df['order_date'].dt.year
    return df


if __name__ == "__main__":
    engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')

    sales = pd.read_csv('data/raw/sales.csv')
    customers = pd.read_csv('data/raw/customers.csv')
    products = pd.read_csv('data/raw/products.csv')
    marketing = pd.read_csv('data/raw/marketing.csv')

    sales = clean_sales_data(sales)
    sales = feature_engineering_sales(sales)
    sales.to_csv('data/cleaned/sales_cleaned.csv', index=False)

    customers = clean_customer_data(customers)
    customers.to_csv('data/cleaned/customers_cleaned.csv', index=False)

    products = clean_product_data(products)
    products.to_csv('data/cleaned/products_cleaned.csv', index=False)

    marketing = clean_marketing_data(marketing)
    marketing.to_csv('data/cleaned/marketing_cleaned.csv', index=False)

    print("Data cleaning completed.")
