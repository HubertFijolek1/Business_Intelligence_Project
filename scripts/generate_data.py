import pandas as pd
from faker import Faker
import numpy as np
import random
from datetime import datetime, timedelta
import os

fake = Faker()

# Constants
NUM_CUSTOMERS = 200
NUM_PRODUCTS = 5
NUM_SALES = 200
NUM_MARKETING_CAMPAIGNS = 20

# Product Details
PRODUCTS = [
    {"product_id": f"P{str(i).zfill(3)}", "product_name": name, "category": category, "price": price, "stock": stock}
    for i, (name, category, price, stock) in enumerate([
        ("Wireless Mouse", "Electronics", 24.99, 150),
        ("Gaming Keyboard", "Electronics", 19.99, 80),
        ("Noise-Cancelling Headphones", "Audio", 39.99, 60),
        ("USB-C Charger", "Accessories", 19.99, 200),
        ("Portable SSD 1TB", "Storage", 59.99, 100),
    ], start=1)
]

PRODUCT_ID_LIST = [product["product_id"] for product in PRODUCTS]
PRODUCT_PRICE_MAP = {product["product_id"]: product["price"] for product in PRODUCTS}


# Segments based on CLV and Number of Orders
def assign_segment(clv, num_orders):
    if clv >= 300 and num_orders >= 10:
        return "Premium"
    elif 150 <= clv < 300 and 5 <= num_orders < 10:
        return "Standard"
    else:
        return "Basic"


# Generate Customers
def generate_customers(num_customers):
    customers = []
    for i in range(1, num_customers + 1):
        customer_id = f"C{str(i).zfill(3)}"
        name = fake.name()
        email = fake.email()
        signup_date = fake.date_between(start_date='-2y', end_date='today')
        # Assume last_order_date is after signup_date
        last_order_date = fake.date_between(start_date=signup_date, end_date='today')
        num_orders = random.randint(1, 20)
        clv = round(random.uniform(20.0, 500.0), 2)
        age = random.randint(18, 65)
        segment = assign_segment(clv, num_orders)

        customers.append({
            "customer_id": customer_id,
            "name": name,
            "email": email,
            "signup_date": signup_date.strftime('%Y-%m-%d'),
            "last_order_date": last_order_date.strftime('%Y-%m-%d'),
            "num_orders": num_orders,
            "CLV": clv,
            "age": age,
            "segment": segment
        })
    return pd.DataFrame(customers)


# Generate Sales
def generate_sales(num_sales, customers, products):
    sales = []
    for i in range(1, num_sales + 1):
        order_id = 1000 + i
        customer = customers.sample(1).iloc[0]
        customer_id = customer["customer_id"]
        product = random.choice(products)
        product_id = product["product_id"]
        quantity = random.randint(1, 5)
        total_price = round(quantity * product["price"], 2)
        # Order date between signup_date and today
        start_date = datetime.strptime(customer["signup_date"], '%Y-%m-%d')
        end_date = datetime.strptime('2024-12-31', '%Y-%m-%d')
        order_date = fake.date_between(start_date=start_date, end_date=end_date)

        sales.append({
            "order_id": order_id,
            "customer_id": customer_id,
            "product_id": product_id,
            "quantity": quantity,
            "total_price": total_price,
            "order_date": order_date.strftime('%Y-%m-%d')
        })
    return pd.DataFrame(sales)


# Generate Marketing Campaigns
def generate_marketing_campaigns(num_campaigns):
    campaign_names = ["Spring Sale", "Summer Promotion", "Black Friday", "Holiday Discounts", "New Year Blast",
                      "Cyber Monday", "Back to School", "Winter Clearance", "Flash Sale", "Exclusive Offer"]
    campaigns = []
    for i in range(1, num_campaigns + 1):
        campaign_id = f"M{str(i).zfill(3)}"
        campaign_name = random.choice(campaign_names)
        spend = round(random.uniform(1000.0, 20000.0), 2)
        # Assume conversions are correlated with spend
        conversions = int(spend / random.uniform(20.0, 50.0))
        start_date = fake.date_between(start_date='-1y', end_date='today')
        # Campaign duration between 7 to 30 days
        duration = random.randint(7, 30)
        end_date = start_date + timedelta(days=duration)
        # Ensure end_date does not exceed '2025-01-31'
        if end_date > datetime.strptime('2025-01-31', '%Y-%m-%d').date():
            end_date = datetime.strptime('2025-01-31', '%Y-%m-%d').date()

        campaigns.append({
            "campaign_id": campaign_id,
            "campaign_name": campaign_name,
            "spend": spend,
            "conversions": conversions,
            "start_date": start_date.strftime('%Y-%m-%d'),
            "end_date": end_date.strftime('%Y-%m-%d')
        })
    return pd.DataFrame(campaigns)


def main():
    # Create raw directory if it doesn't exist
    os.makedirs('../data/raw', exist_ok=True)

    # Generate and save customers
    print("Generating customers...")
    customers_df = generate_customers(NUM_CUSTOMERS)
    customers_df.to_csv('../data/raw/customers.csv', index=False)
    print("customers.csv generated with 200 rows.")

    # Generate and save sales
    print("Generating sales...")
    sales_df = generate_sales(NUM_SALES, customers_df, PRODUCTS)
    sales_df.to_csv('../data/raw/sales.csv', index=False)
    print("sales.csv generated with 200 rows.")

    # Generate and save products
    print("Generating products...")
    products_df = pd.DataFrame(PRODUCTS)
    products_df.to_csv('../data/raw/products.csv', index=False)
    print("products.csv generated with 5 products.")

    # Generate and save marketing campaigns
    print("Generating marketing campaigns...")
    marketing_df = generate_marketing_campaigns(NUM_MARKETING_CAMPAIGNS)
    marketing_df.to_csv('../data/raw/marketing.csv', index=False)
    print("marketing.csv generated with 20 campaigns.")


if __name__ == "__main__":
    main()
