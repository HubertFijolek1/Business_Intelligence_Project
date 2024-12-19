import pandas as pd
from sqlalchemy import create_engine
from database import get_engine
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import numpy as np

def get_monthly_sales_prediction(engine):
    # Query monthly aggregated sales and marketing spend
    query = """
    WITH monthly_sales AS (
        SELECT 
            DATE_TRUNC('month', order_date) AS month,
            SUM(total_price) AS monthly_sales
        FROM sales
        GROUP BY 1
    ),
    monthly_spend AS (
        SELECT
            DATE_TRUNC('month', start_date) AS month,
            SUM(spend) AS monthly_spend
        FROM marketing
        GROUP BY 1
    )
    SELECT ms.month, ms.monthly_sales, COALESCE(mo.monthly_spend,0) AS monthly_spend
    FROM monthly_sales ms
    LEFT JOIN monthly_spend mo ON ms.month = mo.month
    ORDER BY ms.month;
    """
    df = pd.read_sql(query, engine)
    df['month'] = pd.to_datetime(df['month'])
    df.sort_values('month', inplace=True)

    # Prepare features and target
    X = df[['monthly_spend']]
    y = df['monthly_sales']

    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('regressor', LinearRegression())
    ])

    pipeline.fit(X, y)
    df['predicted_sales'] = pipeline.predict(X)

    return df[['month', 'monthly_spend', 'monthly_sales', 'predicted_sales']]