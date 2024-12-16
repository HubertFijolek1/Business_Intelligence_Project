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

elif page == "KPIs":
    st.header("Key Performance Indicators (KPIs)")
    st.write("KPI metrics will be displayed here.")
