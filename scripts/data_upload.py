import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.types import Date, DateTime, Numeric, Integer, String
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


def upload_dataframe_to_postgres(df, table_name, engine):
    try:
        # Define dtype mapping based on table_name
        if table_name == 'sales':
            dtype = {
                'order_id': Integer(),
                'customer_id': String(),
                'product_id': String(),
                'quantity': Integer(),
                'total_price': Numeric(),
                'order_date': Date()  # Specify order_date as Date
            }
        elif table_name == 'customers':
            dtype = {
                'customer_id': String(),
                'name': String(),
                'email': String(),
                'signup_date': Date(),
                'last_order_date': Date(),
                'num_orders': Integer(),
                'CLV': Numeric(),
                'age': Integer(),
                'segment': String()
            }
        elif table_name == 'products':
            dtype = {
                'product_id': String(),
                'product_name': String(),
                'category': String(),
                'price': Numeric(),
                'stock': Integer()
            }
        elif table_name == 'marketing':
            dtype = {
                'campaign_id': String(),
                'campaign_name': String(),
                'spend': Numeric(),
                'conversions': Integer(),
                'impressions': Integer(),
                'start_date': Date(),
                'end_date': Date()
            }
        else:
            dtype = {}

        df.to_sql(table_name, engine, if_exists='replace', index=False, dtype=dtype)
        print(f"Successfully uploaded {table_name} to PostgreSQL.")
    except Exception as e:
        print(f"Error uploading {table_name}: {e}")


def main():
    db_user, db_password, db_host, db_port, db_name = load_environment_variables()
    try:
        engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')
        print("Connected to PostgreSQL successfully.")
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")
        exit(1)

    # Define paths to cleaned CSVs
    data_dir = 'data/cleaned'
    sales_csv = os.path.join(data_dir, 'sales_cleaned.csv')
    customers_csv = os.path.join(data_dir, 'customers_cleaned.csv')
    products_csv = os.path.join(data_dir, 'products_cleaned.csv')
    marketing_csv = os.path.join(data_dir, 'marketing_cleaned.csv')

    # Load CSVs into DataFrames
    try:
        sales_df = pd.read_csv(sales_csv, parse_dates=['order_date'])
        customers_df = pd.read_csv(customers_csv, parse_dates=['signup_date', 'last_order_date'])
        products_df = pd.read_csv(products_csv)
        marketing_df = pd.read_csv(marketing_csv, parse_dates=['start_date', 'end_date'])
    except FileNotFoundError as e:
        print(f"Error reading CSV files: {e}")
        exit(1)
    except Exception as e:
        print(f"Error processing CSV files: {e}")
        exit(1)

    # Upload DataFrames to PostgreSQL
    upload_dataframe_to_postgres(sales_df, 'sales', engine)
    upload_dataframe_to_postgres(customers_df, 'customers', engine)
    upload_dataframe_to_postgres(products_df, 'products', engine)
    upload_dataframe_to_postgres(marketing_df, 'marketing', engine)


if __name__ == "__main__":
    main()
