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

def upload_dataframe_to_postgres(df, table_name, engine):
    try:
        df.to_sql(table_name, engine, if_exists='replace', index=False)
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
        sales_df = pd.read_csv(sales_csv)
        customers_df = pd.read_csv(customers_csv)
        products_df = pd.read_csv(products_csv)
        marketing_df = pd.read_csv(marketing_csv)
    except FileNotFoundError as e:
        print(f"Error reading CSV files: {e}")
        exit(1)

    # Upload DataFrames to PostgreSQL
    upload_dataframe_to_postgres(sales_df, 'sales', engine)
    upload_dataframe_to_postgres(customers_df, 'customers', engine)
    upload_dataframe_to_postgres(products_df, 'products', engine)
    upload_dataframe_to_postgres(marketing_df, 'marketing', engine)

if __name__ == "__main__":
    main()
