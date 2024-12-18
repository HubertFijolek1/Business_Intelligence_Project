import pandas as pd

def apply_filters(sales_df, product_df, customer_df, marketing_df,
                  start_date, end_date, selected_products, selected_segments, selected_campaigns):
    filtered = sales_df.copy()

    if start_date and end_date:
        filtered = filtered[(filtered['order_date'] >= pd.to_datetime(start_date)) &
                            (filtered['order_date'] <= pd.to_datetime(end_date))]

    if 'All' not in selected_products:
        valid_pids = product_df[product_df['product_name'].isin(selected_products)]['product_id']
        filtered = filtered[filtered['product_id'].isin(valid_pids)]

    if 'All' not in selected_segments:
        valid_cids = customer_df[customer_df['segment'].isin(selected_segments)]['customer_id']
        filtered = filtered[filtered['customer_id'].isin(valid_cids)]

    if 'All' not in selected_campaigns:
        try:
            sales_marketing = pd.read_csv("data/cleaned/sales_marketing.csv")
            valid_oids = sales_marketing[sales_marketing['campaign_name'].isin(selected_campaigns)]['order_id']
            filtered = filtered[filtered['order_id'].isin(valid_oids)]
        except FileNotFoundError:
            pass

    return filtered