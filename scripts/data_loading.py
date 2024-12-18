import pandas as pd
from database import get_engine

engine = get_engine()

def load_sales_data(start_date=None, end_date=None, product_ids=None, customer_ids=None):
    query = "SELECT * FROM sales WHERE 1=1"
    if start_date and end_date:
        query += f" AND order_date BETWEEN '{start_date}' AND '{end_date}'"
    if product_ids:
        products_list = ",".join(f"'{p}'" for p in product_ids)
        query += f" AND product_id IN ({products_list})"
    if customer_ids:
        cust_list = ",".join(f"'{c}'" for c in customer_ids)
        query += f" AND customer_id IN ({cust_list})"
    df = pd.read_sql(query, engine)
    df['order_date'] = pd.to_datetime(df['order_date'])
    return df

def load_customer_data():
    df = pd.read_sql("SELECT * FROM customers", engine)
    if 'signup_date' in df.columns:
        df['signup_date'] = pd.to_datetime(df['signup_date'])
    if 'last_order_date' in df.columns:
        df['last_order_date'] = pd.to_datetime(df['last_order_date'])
    return df

def load_product_data():
    df = pd.read_sql("SELECT * FROM products", engine)
    return df

def load_marketing_data():
    df = pd.read_sql("SELECT * FROM marketing", engine)
    if 'start_date' in df.columns:
        df['start_date'] = pd.to_datetime(df['start_date'])
    if 'end_date' in df.columns:
        df['end_date'] = pd.to_datetime(df['end_date'])
    if 'spend' in df.columns and 'conversions' in df.columns and df['spend'].notnull().all():
        df['ROI'] = (df['conversions'] / df['spend']) * 100.0
    return df

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
