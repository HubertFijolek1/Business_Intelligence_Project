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

st.set_page_config(layout="wide")  # Optimize layout for wide screens
st.title("E-commerce BI Dashboard")

tabs = st.tabs(["Home", "Reports", "KPIs"])

# Home Page
with tabs[0]:
    st.header("Welcome to the E-commerce BI Dashboard")
    st.write("Overview of key metrics and insights.")

# Reports Page
with tabs[1]:
    st.header("Sales Trends and Customer Segments")

    # Load cleaned data with date parsing
    sales_data = pd.read_csv("data/cleaned/sales_cleaned.csv", parse_dates=['order_date'])
    marketing_data = pd.read_csv("data/cleaned/marketing_cleaned.csv", parse_dates=['start_date', 'end_date'])
    product_data = pd.read_csv("data/cleaned/products_cleaned.csv")
    customer_data = pd.read_csv("data/cleaned/customers_cleaned.csv")

    # Calculate ROI (Return on Investment)
    marketing_data['ROI'] = (marketing_data['conversions'] / marketing_data['spend']) * 100  # ROI as conversions per $ spent

    # Sidebar-like filters within the Reports tab
    st.sidebar.header("Filters")

    # Dropdown for Product (Multi-select)
    product_options = ['All'] + product_data['product_name'].unique().tolist()
    selected_products = st.sidebar.multiselect("Select Product(s)", product_options, default=['All'])

    # Dropdown for Customer Segment (Multi-select)
    segment_options = ['All'] + customer_data['segment'].unique().tolist()
    selected_segments = st.sidebar.multiselect("Select Customer Segment(s)", segment_options, default=['All'])

    # Dropdown for Marketing Campaign (Multi-select)
    campaign_options = ['All'] + marketing_data['campaign_name'].unique().tolist()
    selected_campaigns = st.sidebar.multiselect("Select Marketing Campaign(s)", campaign_options, default=['All'])

    # Apply Filters
    filtered_sales = sales_data.copy()

    if 'All' not in selected_products:
        filtered_sales = filtered_sales[filtered_sales['product_id'].isin(
            product_data[product_data['product_name'].isin(selected_products)]['product_id']
        )]

    if 'All' not in selected_segments:
        filtered_sales = filtered_sales[filtered_sales['customer_id'].isin(
            customer_data[customer_data['segment'].isin(selected_segments)]['customer_id']
        )]

    if 'All' not in selected_campaigns:
        try:
            sales_marketing = pd.read_csv("data/cleaned/sales_marketing.csv")  # Adjust path as necessary
            campaign_sales_ids = sales_marketing[sales_marketing['campaign_name'].isin(selected_campaigns)]['order_id']
            filtered_sales = filtered_sales[filtered_sales['order_id'].isin(campaign_sales_ids)]
        except FileNotFoundError:
            st.warning("Sales-Marketing mapping file not found. Campaign filtering is disabled.")
        except Exception as e:
            st.error(f"Error applying campaign filters: {e}")

    # Display filtered data metrics
    st.subheader("Filtered Sales Metrics")
    total_sales = filtered_sales['total_price'].sum()
    total_orders = filtered_sales['order_id'].nunique()
    average_order_value = filtered_sales['total_price'].mean()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Sales ($)", f"${total_sales:,.2f}")
    col2.metric("Total Orders", f"{total_orders}")
    col3.metric("Average Order Value (AOV)", f"${average_order_value:,.2f}")

    # Layout Optimization using Columns
    report_columns = st.columns(2)

    # Column 1: Monthly Sales Trends
    with report_columns[0]:
        st.subheader(f"Monthly Sales Trends ({start_date} to {end_date})")
        filtered_sales['month'] = filtered_sales['order_date'].dt.to_period("M").astype(str)
        monthly_sales_filtered = filtered_sales.groupby('month')['total_price'].sum().reset_index()
        fig_sales = px.line(
            monthly_sales_filtered,
            x='month',
            y='total_price',
            title="Filtered Monthly Sales Trends",
            labels={"month": "Month", "total_price": "Total Sales ($)"}
        )
        st.plotly_chart(fig_sales, use_container_width=True)

    # Column 2: Campaign ROI Scatter Plot
    with report_columns[1]:
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
        st.plotly_chart(fig_roi, use_container_width=True)

    # Customer Segmentation
    st.header("Customer Segmentation")
    st.write("Customer Segments: Premium, Standard, Basic")

    segment_distribution = customer_data['segment'].value_counts().reset_index()
    segment_distribution.columns = ['Segment', 'Count']

    # Layout Optimization using Columns
    segmentation_columns = st.columns(2)

    # Column 1: Pie Chart for Customer Segments
    with segmentation_columns[0]:
        st.subheader("Customer Segments Distribution")
        fig_segments = px.pie(segment_distribution, names='Segment', values='Count', title="Customer Segments")
        st.plotly_chart(fig_segments, use_container_width=True)

    # Column 2: Drill-Down Reports
    with segmentation_columns[1]:
        st.subheader("Drill-Down: Campaign Details")
        selected_campaign = st.selectbox("Select a Campaign for Detailed Insights", options=marketing_data['campaign_name'].unique())

        if selected_campaign:
            campaign_details = marketing_data[marketing_data['campaign_name'] == selected_campaign]
            st.write("#### Campaign Details")
            st.write(campaign_details)

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

    # Product Performance
    st.header("Product Performance")
    st.write("Product Performance by Revenue and Quantity Sold")

    sales_with_products = filtered_sales.merge(product_data, on='product_id')

    product_performance = sales_with_products.groupby('product_name').agg(
        total_revenue=('total_price', 'sum'),
        total_quantity=('quantity', 'sum')
    ).reset_index()

    # Layout Optimization using Columns
    performance_columns = st.columns(2)

    # Column 1: Bar Chart for Product Revenue
    with performance_columns[0]:
        st.subheader("Product Revenue")
        fig_revenue = px.bar(product_performance, x='product_name', y='total_revenue', title="Product Revenue")
        st.plotly_chart(fig_revenue, use_container_width=True)

    # Column 2: Bar Chart for Quantity Sold
    with performance_columns[1]:
        st.subheader("Product Quantity Sold")
        fig_quantity = px.bar(product_performance, x='product_name', y='total_quantity', title="Product Quantity Sold")
        st.plotly_chart(fig_quantity, use_container_width=True)

    st.header("Campaign ROI Analysis")

    if 'ROI' not in marketing_data.columns:
        marketing_data['ROI'] = (marketing_data['conversions'] / marketing_data['spend']) * 100  # ROI as conversions per $ spent

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
    st.plotly_chart(fig_roi, use_container_width=True)

    st.header("Campaign Drill-Down Reports")

    selected_campaign = st.selectbox("Select a Campaign for Detailed Insights", options=marketing_data['campaign_name'].unique())

    if selected_campaign:
        campaign_details = marketing_data[marketing_data['campaign_name'] == selected_campaign]
        st.write("#### Campaign Details")
        st.write(campaign_details)

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

    # Create columns for KPIs
    kpi_columns = st.columns(3)

    # Display KPIs with st.metric within columns
    kpi_columns[0].metric("Customer Acquisition Cost (CAC)", f"${kpis['Customer Acquisition Cost (CAC)']:.2f}")
    kpi_columns[1].metric("Customer Lifetime Value (CLV)", f"${kpis['Customer Lifetime Value (CLV)']:.2f}")
    kpi_columns[2].metric("Conversion Rate (%)", f"{kpis['Conversion Rate (%)']:.2f}")

    # Add another row of KPIs
    kpi_columns_2 = st.columns(2)
    kpi_columns_2[0].metric("Sales Growth Rate (%)", f"{kpis['Sales Growth Rate (%)']:.2f}")
    kpi_columns_2[1].metric("Average Order Value (AOV)", f"${kpis['Average Order Value (AOV)']:.2f}")

    # Optional: Add detailed KPI charts or drill-downs
    st.subheader("Sales Growth Over Time")
    sales_growth_data = pd.read_sql("""
        SELECT 
            EXTRACT(YEAR FROM order_date) AS year,
            EXTRACT(MONTH FROM order_date) AS month,
            SUM(total_price) AS monthly_sales
        FROM sales
        GROUP BY year, month
        ORDER BY year, month
    """, engine)
    sales_growth_data['year_month'] = sales_growth_data.apply(lambda row: f"{int(row['year'])}-{int(row['month']):02d}", axis=1)
    fig_growth = px.line(
        sales_growth_data,
        x='year_month',
        y='monthly_sales',
        title="Sales Growth Over Time",
        labels={"year_month": "Year-Month", "monthly_sales": "Monthly Sales ($)"}
    )
    st.plotly_chart(fig_growth, use_container_width=True)
