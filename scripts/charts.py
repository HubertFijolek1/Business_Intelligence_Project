import plotly.express as px

def monthly_sales_trend_chart(filtered_sales, start_date, end_date):
    filtered_sales['month'] = filtered_sales['order_date'].dt.to_period("M").astype(str)
    monthly_sales_filtered = filtered_sales.groupby('month')['total_price'].sum().reset_index()
    fig = px.line(
        monthly_sales_filtered,
        x='month',
        y='total_price',
        title=f"Monthly Sales Trends ({start_date} to {end_date})",
        labels={"month": "Month", "total_price": "Total Sales ($)"}
    )
    return fig

def campaign_spend_vs_conversions(marketing_data):
    fig = px.scatter(
        marketing_data,
        x='spend',
        y='conversions',
        color='campaign_name',
        size='impressions',
        hover_data=['campaign_id', 'ROI'],
        title="Campaign Spend vs. Conversions"
    )
    fig.update_traces(marker=dict(opacity=0.7, line=dict(width=1, color='DarkSlateGrey')))
    return fig

def customer_segments_pie(segment_distribution):
    fig = px.pie(segment_distribution, names='Segment', values='Count', title="Customer Segments")
    return fig

def product_revenue_bar(product_performance):
    fig = px.bar(product_performance, x='product_name', y='total_revenue', title="Product Revenue")
    return fig

def product_quantity_bar(product_performance):
    fig = px.bar(product_performance, x='product_name', y='total_quantity', title="Product Quantity Sold")
    return fig

def sales_growth_over_time_chart(sales_growth_data):
    fig = px.line(
        sales_growth_data,
        x='year_month',
        y='monthly_sales',
        title="Sales Growth Over Time",
        labels={"year_month": "Year-Month", "monthly_sales": "Monthly Sales ($)"}
    )
    return fig
