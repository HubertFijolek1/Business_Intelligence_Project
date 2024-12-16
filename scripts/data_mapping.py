import pandas as pd
import os


def generate_sales_marketing_mapping(sales_cleaned_path, marketing_cleaned_path, output_path):
    """
    Generates a sales-marketing mapping CSV by associating each order with active marketing campaigns.

    Parameters:
    - sales_cleaned_path: Path to the cleaned sales CSV file.
    - marketing_cleaned_path: Path to the cleaned marketing CSV file.
    - output_path: Path where the sales_marketing.csv will be saved.
    """
    # Load the cleaned sales and marketing data
    sales = pd.read_csv(sales_cleaned_path, parse_dates=['order_date'])
    marketing = pd.read_csv(marketing_cleaned_path, parse_dates=['start_date', 'end_date'])

    # Initialize an empty list to store mappings
    mappings = []

    # Iterate over each sale to find applicable campaigns
    for _, order in sales.iterrows():
        order_id = order['order_id']
        order_date = order['order_date']

        # Find campaigns active on the order_date
        active_campaigns = marketing[
            (marketing['start_date'] <= order_date) &
            (marketing['end_date'] >= order_date)
            ]

        # If there are active campaigns, map the order to each campaign
        if not active_campaigns.empty:
            for _, campaign in active_campaigns.iterrows():
                mappings.append({
                    'order_id': order_id,
                    'campaign_name': campaign['campaign_name']
                })
        else:
            # Optionally, map to 'No Campaign' or skip
            mappings.append({
                'order_id': order_id,
                'campaign_name': 'No Campaign'
            })

    # Create a DataFrame from the mappings
    sales_marketing = pd.DataFrame(mappings)

    # Remove potential duplicates
    sales_marketing.drop_duplicates(inplace=True)

    # Save the mapping to CSV
    sales_marketing.to_csv(output_path, index=False)
    print(f"sales_marketing.csv generated with {len(sales_marketing)} mappings at {output_path}.")


def main():
    # Define paths
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_CLEANED_DIR = os.path.join(SCRIPT_DIR, '..', 'data', 'cleaned')

    sales_cleaned_path = os.path.join(DATA_CLEANED_DIR, 'sales_cleaned.csv')
    marketing_cleaned_path = os.path.join(DATA_CLEANED_DIR, 'marketing_cleaned.csv')
    output_path = os.path.join(DATA_CLEANED_DIR, 'sales_marketing.csv')

    # Check if input files exist
    if not os.path.exists(sales_cleaned_path):
        print(f"Error: {sales_cleaned_path} does not exist. Please run data_cleaning.py first.")
        return
    if not os.path.exists(marketing_cleaned_path):
        print(f"Error: {marketing_cleaned_path} does not exist. Please run data_cleaning.py first.")
        return

    # Generate the mapping
    generate_sales_marketing_mapping(sales_cleaned_path, marketing_cleaned_path, output_path)


if __name__ == "__main__":
    main()
