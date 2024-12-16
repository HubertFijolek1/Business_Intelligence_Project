import streamlit as st
import pandas as pd
import plotly.express as px

st.title("E-commerce BI Dashboard")

st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Select Page", ["Home", "Reports", "KPIs"])

if page == "Home":
    st.header("Welcome to the E-commerce BI Dashboard")
    st.write("Overview of key metrics and insights.")

elif page == "Reports":
    st.header("Sales Trends")
    st.write("Monthly Sales Trends Visualization")

    # Load cleaned sales data
    sales_data = pd.read_csv("data/cleaned/sales_cleaned.csv")
    sales_data['order_date'] = pd.to_datetime(sales_data['order_date'])
    sales_data['month'] = sales_data['order_date'].dt.to_period("M").astype(str)
    monthly_sales = sales_data.groupby('month')['total_price'].sum().reset_index()

    # Line chart for sales trends
    fig = px.line(monthly_sales, x='month', y='total_price', title="Monthly Sales Trends", labels={
        "month": "Month",
        "total_price": "Total Sales ($)"
    })
    st.plotly_chart(fig)

    st.header("Customer Segmentation")
    st.write("Customer Segments: Premium, Standard, Basic")

    # Load cleaned customer data
    customer_data = pd.read_csv("data/cleaned/customers_cleaned.csv")
    segment_distribution = customer_data['segment'].value_counts().reset_index()
    segment_distribution.columns = ['Segment', 'Count']

    # Pie chart for customer segments
    fig = px.pie(segment_distribution, names='Segment', values='Count', title="Customer Segmentation")
    st.plotly_chart(fig)

    st.header("Product Performance")
    st.write("Product Performance by Revenue and Quantity Sold")

    # Load cleaned product and sales data
    product_data = pd.read_csv("data/cleaned/products_cleaned.csv")
    sales_with_products = sales_data.merge(product_data, on='product_id')

    product_performance = sales_with_products.groupby('product_name').agg(
        total_revenue=('total_price', 'sum'),
        total_quantity=('quantity', 'sum')
    ).reset_index()

    # Bar chart for revenue
    fig_revenue = px.bar(product_performance, x='product_name', y='total_revenue', title="Product Revenue")
    st.plotly_chart(fig_revenue)

    # Bar chart for quantity sold
    fig_quantity = px.bar(product_performance, x='product_name', y='total_quantity', title="Product Quantity Sold")
    st.plotly_chart(fig_quantity)

elif page == "KPIs":
    st.header("Key Performance Indicators (KPIs)")
    st.write("KPI metrics will be displayed here.")
