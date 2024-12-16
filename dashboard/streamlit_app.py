import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import sys

# Add the scripts directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts")))
import kpi_calculations

# Load environment variables
load_dotenv()

db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')

engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')

st.title("E-commerce BI Dashboard")

tabs = st.tabs(["Home", "Reports", "KPIs"])


# Home Page
with tabs[0]:
    st.header("Welcome to the E-commerce BI Dashboard")
    st.write("Overview of key metrics and insights.")

# Reports Page
with tabs[1]:
    st.header("Sales Trends and Customer Segments")

    # Load cleaned sales data
    sales_data = pd.read_csv("data/cleaned/sales_cleaned.csv")
    sales_data['order_date'] = pd.to_datetime(sales_data['order_date'])

    # Sidebar Date Range Filter
    st.sidebar.subheader("Filter by Date Range")
    start_date = st.sidebar.date_input("Start Date", sales_data['order_date'].min())
    end_date = st.sidebar.date_input("End Date", sales_data['order_date'].max())

    # Filter sales data based on the date range
    filtered_sales = sales_data[
        (sales_data['order_date'] >= pd.to_datetime(start_date)) &
        (sales_data['order_date'] <= pd.to_datetime(end_date))
    ]

    # Monthly Sales Trends (Filtered)
    filtered_sales['month'] = filtered_sales['order_date'].dt.to_period("M").astype(str)
    monthly_sales_filtered = filtered_sales.groupby('month')['total_price'].sum().reset_index()

    # Line chart for filtered sales trends
    st.subheader(f"Monthly Sales Trends ({start_date} to {end_date})")
    fig_sales = px.line(
        monthly_sales_filtered,
        x='month',
        y='total_price',
        title="Filtered Monthly Sales Trends",
        labels={"month": "Month", "total_price": "Total Sales ($)"}
    )
    st.plotly_chart(fig_sales)

    # Customer Segmentation
    st.header("Customer Segmentation")
    st.write("Customer Segments: Premium, Standard, Basic")

    customer_data = pd.read_csv("data/cleaned/customers_cleaned.csv")
    segment_distribution = customer_data['segment'].value_counts().reset_index()
    segment_distribution.columns = ['Segment', 'Count']

    # Pie chart for customer segments
    fig_segments = px.pie(segment_distribution, names='Segment', values='Count', title="Customer Segments")
    st.plotly_chart(fig_segments)

    # Product Performance
    st.header("Product Performance")
    st.write("Product Performance by Revenue and Quantity Sold")

    product_data = pd.read_csv("data/cleaned/products_cleaned.csv")
    sales_with_products = filtered_sales.merge(product_data, on='product_id')

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

    st.header("Campaign ROI Analysis")

    # Load cleaned marketing data
    marketing_data = pd.read_csv("data/cleaned/marketing_cleaned.csv")
    marketing_data['start_date'] = pd.to_datetime(marketing_data['start_date'])
    marketing_data['end_date'] = pd.to_datetime(marketing_data['end_date'])

    # Calculate ROI (Return on Investment)
    marketing_data['ROI'] = (marketing_data['conversions'] / marketing_data[
        'spend']) * 100  # ROI as conversions per $ spent

    # Scatter Plot: Spend vs Conversions
    st.subheader("Campaign Spend vs. Conversions")
    fig_roi = px.scatter(
        marketing_data,
        x='spend',
        y='conversions',
        color='campaign_name',
        size='impressions',
        hover_data=['campaign_id', 'ROI'],
        title="Campaign Spend vs. Conversions",
        labels={
            "spend": "Spend ($)",
            "conversions": "Conversions",
            "impressions": "Impressions",
            "campaign_name": "Campaign Name"
        }
    )
    fig_roi.update_traces(marker=dict(opacity=0.7, line=dict(width=1, color='DarkSlateGrey')))
    st.plotly_chart(fig_roi)

    st.header("Campaign Drill-Down Reports")

    # Select Campaign for Drill-Down
    selected_campaign = st.selectbox("Select a Campaign for Detailed Insights",
                                     options=marketing_data['campaign_name'].unique())

    if selected_campaign:
        campaign_details = marketing_data[marketing_data['campaign_name'] == selected_campaign]
        st.write("#### Campaign Details")
        st.write(campaign_details)

        # Load or create sales_marketing mapping
        try:
            sales_marketing = pd.read_csv("data/cleaned/sales_marketing.csv")
            related_order_ids = sales_marketing[sales_marketing['campaign_name'] == selected_campaign]['order_id']
            related_sales = filtered_sales[filtered_sales['order_id'].isin(related_order_ids)]
            st.write("#### Sales Related to Selected Campaign")
            st.write(related_sales)
        except FileNotFoundError:
            st.warning("Sales-Marketing mapping file not found. Drill-down for campaigns is disabled.")
        except Exception as e:
            st.error(f"Error loading sales-marketing mapping: {e}")
# KPIs Page
with tabs[2]:
    st.header("Key Performance Indicators (KPIs)")
    st.write("Live KPI Metrics Summary")

    # Calculate KPIs using imported functions
    kpis = kpi_calculations.calculate_all_kpis(engine)

    # Display KPIs with st.metric
    st.metric("Customer Acquisition Cost (CAC)", f"${kpis['Customer Acquisition Cost (CAC)']:.2f}")
    st.metric("Customer Lifetime Value (CLV)", f"${kpis['Customer Lifetime Value (CLV)']:.2f}")
    st.metric("Conversion Rate (%)", f"{kpis['Conversion Rate (%)']:.2f}")
    st.metric("Sales Growth Rate (%)", f"{kpis['Sales Growth Rate (%)']:.2f}")
    st.metric("Average Order Value (AOV)", f"${kpis['Average Order Value (AOV)']:.2f}")
