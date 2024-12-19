import streamlit as st
import pandas as pd
from streamlit.cache_data import cache_data
from database import get_engine
from filters import apply_filters
import kpi_calculations
from data_loading import load_sales_data, load_customer_data, load_product_data, load_marketing_data
from charts import (
    monthly_sales_trend_chart,
    campaign_spend_vs_conversions,
    customer_segments_pie,
    product_revenue_bar,
    product_quantity_bar,
    sales_growth_over_time_chart
)
from predictive_analysis import get_monthly_sales_prediction

engine = get_engine()

st.set_page_config(layout="wide")
st.title("E-commerce BI Dashboard")

@cache_data
def get_base_data():
    customers = load_customer_data()
    products = load_product_data()
    marketing = load_marketing_data()
    return customers, products, marketing

customers, products, marketing = get_base_data()

product_options = ['All'] + products['product_name'].unique().tolist()
segment_options = ['All'] + customers['segment'].unique().tolist()
campaign_options = ['All'] + marketing['campaign_name'].unique().tolist()

tabs = st.tabs(["Home", "Reports", "KPIs", "Predictive Analysis"])

with tabs[0]:
    st.header("Welcome to the E-commerce BI Dashboard!")
    st.write("This dashboard provides key insights from our e-commerce data.")

# Reports Page
with tabs[1]:
    st.header("Sales Trends and Customer Segments")

    # Sidebar filters
    st.sidebar.header("Filters")
    start_date = st.sidebar.date_input("Start Date", value=None)
    end_date = st.sidebar.date_input("End Date", value=None)
    selected_products = st.sidebar.multiselect("Select Product(s)", product_options, default=['All'])
    selected_segments = st.sidebar.multiselect("Select Customer Segment(s)", segment_options, default=['All'])
    selected_campaigns = st.sidebar.multiselect("Select Marketing Campaign(s)", campaign_options, default=['All'])

    if start_date and end_date and start_date > end_date:
        st.sidebar.error("Error: Start Date must be before End Date.")
    else:
        all_sales = load_sales_data()  # Load all sales first
        filtered_sales = apply_filters(all_sales, products, customers, marketing,
                                       start_date, end_date, selected_products, selected_segments, selected_campaigns)

        if filtered_sales.empty:
            st.warning("No data available for the selected filters.")
        else:
            # Display filtered metrics
            st.subheader("Filtered Sales Metrics")
            total_sales = filtered_sales['total_price'].sum()
            total_orders = filtered_sales['order_id'].nunique()
            average_order_value = filtered_sales['total_price'].mean()

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Sales ($)", f"${total_sales:,.2f}")
            col2.metric("Total Orders", f"{total_orders}")
            col3.metric("Average Order Value (AOV)", f"${average_order_value:,.2f}")

            # Monthly Sales Trends
            report_columns = st.columns(2)
            with report_columns[0]:
                st.subheader("Monthly Sales Trends")
                fig_sales = monthly_sales_trend_chart(filtered_sales, start_date, end_date)
                st.plotly_chart(fig_sales, use_container_width=True)

            with report_columns[1]:
                st.subheader("Campaign Spend vs. Conversions")
                fig_roi = campaign_spend_vs_conversions(marketing)
                st.plotly_chart(fig_roi, use_container_width=True)

            # Customer Segmentation
            st.header("Customer Segmentation")
            st.write("Customer Segments: Premium, Standard, Basic")

            segment_distribution = customers['segment'].value_counts().reset_index()
            segment_distribution.columns = ['Segment', 'Count']

            segmentation_columns = st.columns(2)
            with segmentation_columns[0]:
                st.subheader("Customer Segments Distribution")
                fig_segments = customer_segments_pie(segment_distribution)
                st.plotly_chart(fig_segments, use_container_width=True)

            with segmentation_columns[1]:
                st.subheader("Drill-Down: Campaign Details")
                selected_campaign_seg = st.selectbox(
                    "Select a Campaign for Segmentation Insights",
                    options=marketing['campaign_name'].unique()
                )
                if selected_campaign_seg:
                    campaign_details_seg = marketing[marketing['campaign_name'] == selected_campaign_seg]
                    st.write("#### Campaign Details")
                    st.write(campaign_details_seg)
                    try:
                        sales_marketing = pd.read_csv("data/cleaned/sales_marketing.csv")
                        related_order_ids_seg = sales_marketing[sales_marketing['campaign_name'] == selected_campaign_seg]['order_id']
                        related_sales_seg = filtered_sales[filtered_sales['order_id'].isin(related_order_ids_seg)]
                        st.write("#### Sales Related to Selected Campaign")
                        st.write(related_sales_seg)
                    except FileNotFoundError:
                        st.warning("Sales-Marketing mapping file not found. Drill-down for campaigns is disabled.")

            # Product Performance
            st.header("Product Performance")
            st.write("Product Performance by Revenue and Quantity Sold")

            sales_with_products = filtered_sales.merge(products, on='product_id')
            product_performance = sales_with_products.groupby('product_name').agg(
                total_revenue=('total_price', 'sum'),
                total_quantity=('quantity', 'sum')
            ).reset_index()

            performance_columns = st.columns(2)
            with performance_columns[0]:
                st.subheader("Product Revenue")
                fig_revenue = product_revenue_bar(product_performance)
                st.plotly_chart(fig_revenue, use_container_width=True)

            with performance_columns[1]:
                st.subheader("Product Quantity Sold")
                fig_quantity = product_quantity_bar(product_performance)
                st.plotly_chart(fig_quantity, use_container_width=True)

            # Campaign ROI Analysis
            st.header("Campaign ROI Analysis")
            st.subheader("Campaign Spend vs. Conversions")
            fig_roi_analysis = campaign_spend_vs_conversions(marketing)
            st.plotly_chart(fig_roi_analysis, use_container_width=True)

            # Campaign Drill-Down Reports
            st.header("Campaign Drill-Down Reports")
            selected_campaign_drill = st.selectbox(
                "Select a Campaign for Detailed Insights",
                options=marketing['campaign_name'].unique()
            )
            if selected_campaign_drill:
                campaign_details_drill = marketing[marketing['campaign_name'] == selected_campaign_drill]
                st.write("#### Campaign Details")
                st.write(campaign_details_drill)
                try:
                    sales_marketing = pd.read_csv("data/cleaned/sales_marketing.csv")
                    related_order_ids_drill = sales_marketing[sales_marketing['campaign_name'] == selected_campaign_drill]['order_id']
                    related_sales_drill = filtered_sales[filtered_sales['order_id'].isin(related_order_ids_drill)]
                    st.write("#### Sales Related to Selected Campaign")
                    st.write(related_sales_drill)
                except FileNotFoundError:
                    st.warning("Sales-Marketing mapping file not found. Drill-down for campaigns is disabled.")

# KPIs Page
with tabs[2]:
    st.header("Key Performance Indicators (KPIs)")
    st.write("Live KPI Metrics Summary")

    kpis = kpi_calculations.calculate_all_kpis(engine)

    kpi_columns = st.columns(3)
    kpi_columns[0].metric("Customer Acquisition Cost (CAC)", f"${kpis['Customer Acquisition Cost (CAC)']:.2f}")
    kpi_columns[1].metric("Customer Lifetime Value (CLV)", f"${kpis['Customer Lifetime Value (CLV)']:.2f}")
    kpi_columns[2].metric("Conversion Rate (%)", f"{kpis['Conversion Rate (%)']:.2f}")

    kpi_columns_2 = st.columns(2)
    kpi_columns_2[0].metric("Sales Growth Rate (%)", f"{kpis['Sales Growth Rate (%)']:.2f}")
    kpi_columns_2[1].metric("Average Order Value (AOV)", f"${kpis['Average Order Value (AOV)']:.2f}")

    # Sales Growth Over Time
    sales_growth_data = pd.read_sql("""
        SELECT 
            EXTRACT(YEAR FROM order_date) AS year,
            EXTRACT(MONTH FROM order_date) AS month,
            SUM(total_price) AS monthly_sales
        FROM sales
        GROUP BY EXTRACT(YEAR FROM order_date), EXTRACT(MONTH FROM order_date)
        ORDER BY EXTRACT(YEAR FROM order_date), EXTRACT(MONTH FROM order_date)
    """, engine)
    sales_growth_data['year_month'] = sales_growth_data.apply(lambda row: f"{int(row['year'])}-{int(row['month']):02d}", axis=1)
    fig_growth = sales_growth_over_time_chart(sales_growth_data)
    st.plotly_chart(fig_growth, use_container_width=True)

with tabs[3]:
    st.header("Predictive Analysis (Hyperparameter Tuning)")
    st.write("We've added polynomial features and tuned them using GridSearchCV.")
    prediction_df, cv_score, best_params = get_monthly_sales_prediction(engine)
    st.write("### Best Model Parameters:", best_params)
    st.write("Cross-Validation RMSE:", cv_score)
    st.dataframe(prediction_df)
