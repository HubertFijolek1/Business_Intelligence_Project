import pandas as pd
from sqlalchemy import create_engine


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
    engine = create_engine('postgresql://bi_user:secure_password@localhost:5432/bi_ecommerce')
    sales = load_sales_data(engine)
    customers = load_customer_data(engine)
    products = load_product_data(engine)
    marketing = load_marketing_data(engine)

    sales.to_csv('data/raw/sales.csv', index=False)
    customers.to_csv('data/raw/customers.csv', index=False)
    products.to_csv('data/raw/products.csv', index=False)
    marketing.to_csv('data/raw/marketing.csv', index=False)

    print("Data loaded successfully.")
