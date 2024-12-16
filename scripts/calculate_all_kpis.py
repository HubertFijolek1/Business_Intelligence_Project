import pandas as pd
from sqlalchemy import create_engine

def calculate_cac(engine):
    marketing_spend = pd.read_sql("SELECT SUM(spend) AS total_spend FROM marketing", engine).iloc[0]['total_spend']
    new_customers = pd.read_sql("SELECT COUNT(*) AS new_customers FROM customers WHERE signup_date >= '2024-01-01'", engine).iloc[0]['new_customers']
    cac = marketing_spend / new_customers if new_customers else 0
    return cac

def calculate_clv(engine):
    avg_order_value = pd.read_sql("SELECT AVG(total_price) AS avg_order FROM sales", engine).iloc[0]['avg_order']
    avg_num_orders = pd.read_sql("""
        SELECT AVG(order_count) AS avg_orders
        FROM (
            SELECT COUNT(*) AS order_count
            FROM sales
            GROUP BY customer_id
        ) AS sub
    """, engine).iloc[0]['avg_orders']
    clv = avg_order_value * avg_num_orders
    return clv

def calculate_conversion_rate(engine):
    total_clicks = pd.read_sql("SELECT SUM(clicks) AS total_clicks FROM marketing", engine).iloc[0]['total_clicks']
    total_conversions = pd.read_sql("SELECT SUM(conversions) AS total_conversions FROM marketing", engine).iloc[0]['total_conversions']
    conversion_rate = (total_conversions / total_clicks) * 100 if total_clicks else 0
    return conversion_rate

def calculate_sales_growth_rate(engine, current_year=2024):
    current_sales = pd.read_sql(f"SELECT SUM(total_price) AS current_sales FROM sales WHERE EXTRACT(YEAR FROM order_date) = {current_year}", engine).iloc[0]['current_sales']
    previous_sales = pd.read_sql(f"SELECT SUM(total_price) AS previous_sales FROM sales WHERE EXTRACT(YEAR FROM order_date) = {current_year - 1}", engine).iloc[0]['previous_sales']
    growth_rate = ((current_sales - previous_sales) / previous_sales) * 100 if previous_sales else 0
    return growth_rate

def calculate_aov(engine):
    aov = pd.read_sql("SELECT AVG(total_price) AS aov FROM sales", engine).iloc[0]['aov']
    return aov

def calculate_all_kpis(engine):
    kpis = {
        "Customer Acquisition Cost (CAC)": calculate_cac(engine),
        "Customer Lifetime Value (CLV)": calculate_clv(engine),
        "Conversion Rate (%)": calculate_conversion_rate(engine),
        "Sales Growth Rate (%)": calculate_sales_growth_rate(engine),
        "Average Order Value (AOV)": calculate_aov(engine)
    }
    return kpis
