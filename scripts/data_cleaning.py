# scripts/data_cleaning.py

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
    df['last_order_date'] = pd.to_datetime(df['last_order_date'])
    return df


def clean_product_data(df):
    df.dropna(subset=['product_id', 'product_name', 'price'], inplace=True)
    return df


def clean_marketing_data(df):
    df.dropna(subset=['campaign_id', 'campaign_name', 'spend', 'conversions', 'impressions'], inplace=True)
    df['start_date'] = pd.to_datetime(df['start_date'])
    df['end_date'] = pd.to_datetime(df['end_date'])
    return df


def feature_engineering_sales(df):
    df['month'] = df['order_date'].dt.month
    df['year'] = df['order_date'].dt.year
    return df


def generate_sales_marketing_mapping(sales_df, marketing_df):
    """
    Generates a sales-marketing mapping DataFrame by associating each order with active marketing campaigns.

    Parameters:
    - sales_df: Cleaned sales DataFrame.
    - marketing_df: Cleaned marketing DataFrame.

    Returns:
    - sales_marketing_df: DataFrame with 'order_id' and 'campaign_name'.
    """
    mappings = []

    for _, order in sales_df.iterrows():
        order_id = order['order_id']
        order_date = order['order_date']

        # Find campaigns active on the order_date
        active_campaigns = marketing_df[
            (marketing_df['start_date'] <= order_date) &
            (marketing_df['end_date'] >= order_date)
            ]

        if not active_campaigns.empty:
            for _, campaign in active_campaigns.iterrows():
                mappings.append({
                    'order_id': order_id,
                    'campaign_name': campaign['campaign_name']
                })
        else:
            mappings.append({
                'order_id': order_id,
                'campaign_name': 'No Campaign'
            })

    sales_marketing_df = pd.DataFrame(mappings)
    sales_marketing_df.drop_duplicates(inplace=True)

    return sales_marketing_df


if __name__ == "__main__":
    # Read raw CSVs
    sales = pd.read_csv('data/raw/sales.csv')
    customers = pd.read_csv('data/raw/customers.csv')
    products = pd.read_csv('data/raw/products.csv')
    marketing = pd.read_csv('data/raw/marketing.csv')

    # Clean data
    sales = clean_sales_data(sales)
    sales = feature_engineering_sales(sales)
    customers = clean_customer_data(customers)
    products = clean_product_data(products)
    marketing = clean_marketing_data(marketing)

    # Save cleaned data
    sales.to_csv('data/cleaned/sales_cleaned.csv', index=False)
    customers.to_csv('data/cleaned/customers_cleaned.csv', index=False)
    products.to_csv('data/cleaned/products_cleaned.csv', index=False)
    marketing.to_csv('data/cleaned/marketing_cleaned.csv', index=False)

    print("Data cleaning completed.")

    # Generate sales-marketing mapping
    sales_marketing = generate_sales_marketing_mapping(sales, marketing)
    sales_marketing.to_csv('data/cleaned/sales_marketing.csv', index=False)
    print("Sales-Marketing mapping completed and saved to sales_marketing.csv.")
