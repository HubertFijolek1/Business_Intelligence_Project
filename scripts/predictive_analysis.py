import pandas as pd
from scripts.database import get_engine
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import mean_squared_error, make_scorer
import numpy as np

def get_monthly_sales_prediction(engine):
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
    df['month'] = pd.to_datetime(df['month'], errors='coerce', utc=True)
    df.dropna(subset=['month'], inplace=True)
    df['month'] = df['month'].dt.tz_convert(None)
    df.sort_values('month', inplace=True)

    X = df[['monthly_spend']]
    y = df['monthly_sales']

    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('poly', PolynomialFeatures()),
        ('regressor', LinearRegression())
    ])

    param_grid = {
        'poly__degree': [1, 2, 3]
    }

    mse_scorer = make_scorer(mean_squared_error, greater_is_better=False)
    grid_search = GridSearchCV(pipeline, param_grid, scoring=mse_scorer, cv=3)
    grid_search.fit(X, y)

    best_model = grid_search.best_estimator_
    y_pred = best_model.predict(X)

    rmse = np.sqrt(mean_squared_error(y, y_pred))

    df['predicted_sales'] = y_pred
    return df[['month', 'monthly_spend', 'monthly_sales', 'predicted_sales']], rmse, grid_search.best_params_
