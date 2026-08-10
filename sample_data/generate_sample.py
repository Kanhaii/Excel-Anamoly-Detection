"""
Generate sample business data with injected anomalies.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

def generate_sample_data(days: int = 365) -> pd.DataFrame:
    """
    Generate realistic sample business data with anomalies.
    
    Args:
        days: Number of days of data to generate
    
    Returns:
        DataFrame with sample data
    """
    np.random.seed(42)
    
    dates = [datetime(2023, 1, 1) + timedelta(days=x) for x in range(days)]
    
    # Generate base metrics
    traffic = np.random.normal(10000, 1500, days) + 500 * np.sin(np.arange(days) * 2 * np.pi / 365)
    traffic = np.maximum(traffic, 5000)  # Floor at 5000
    
    conversion_rate = np.random.normal(3.5, 0.5, days)
    conversion_rate = np.maximum(conversion_rate, 1.0)  # Floor at 1%
    
    orders = (traffic * conversion_rate / 100).astype(int)
    orders = np.maximum(orders, 50)  # Floor at 50
    
    revenue = orders * np.random.normal(75, 15, days)
    revenue = np.maximum(revenue, 0)
    
    cost = revenue * np.random.uniform(0.3, 0.5, days)
    profit = revenue - cost
    
    refunds = orders * np.random.uniform(0.02, 0.08, days)
    customers = np.random.randint(50, 500, days)
    
    # Create DataFrame
    df = pd.DataFrame({
        'Date': dates,
        'Traffic': traffic.astype(int),
        'Orders': orders,
        'Conversion_Rate': conversion_rate,
        'Revenue': revenue.astype(int),
        'Cost': cost.astype(int),
        'Profit': profit.astype(int),
        'Refunds': refunds.astype(int),
        'Customers': customers
    })
    
    # Inject anomalies
    # Anomaly 1: Traffic spike and conversion drop (around day 200)
    if days > 200:
        df.loc[200:210, 'Traffic'] = (df.loc[200:210, 'Traffic'] * 1.35).astype(int)
        df.loc[200:210, 'Conversion_Rate'] = df.loc[200:210, 'Conversion_Rate'] * 0.75
        df.loc[200:210, 'Orders'] = (df.loc[200:210, 'Traffic'] * df.loc[200:210, 'Conversion_Rate'] / 100).astype(int)
    
    # Anomaly 2: Revenue drop (around day 250)
    if days > 250:
        df.loc[250:260, 'Revenue'] = (df.loc[250:260, 'Revenue'] * 0.70).astype(int)
        df.loc[250:260, 'Profit'] = df.loc[250:260, 'Revenue'] - df.loc[250:260, 'Cost']
    
    # Anomaly 3: Refunds spike (around day 300)
    if days > 300:
        df.loc[300:310, 'Refunds'] = (df.loc[300:310, 'Refunds'] * 2.5).astype(int)
    
    # Anomaly 4: Cost increase while revenue flat (around day 330)
    if days > 330:
        df.loc[330:340, 'Cost'] = (df.loc[330:340, 'Cost'] * 1.4).astype(int)
        df.loc[330:340, 'Profit'] = df.loc[330:340, 'Revenue'] - df.loc[330:340, 'Cost']
    
    return df

def save_sample_data(output_path: Path) -> None:
    """
    Generate and save sample data to Excel.
    
    Args:
        output_path: Path to save Excel file
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    df = generate_sample_data(365)
    df.to_excel(output_path, sheet_name='Business Metrics', index=False)
    
    print(f"✅ Sample data saved to {output_path}")
    print(f"   - {len(df)} rows, {len(df.columns)} columns")
    print(f"   - Columns: {', '.join(df.columns)}")
    print(f"   - Intentional anomalies: Traffic spike, Revenue drop, Refund increase, Cost jump")

if __name__ == "__main__":
    from config.settings import SAMPLE_DATA_PATH
    save_sample_data(SAMPLE_DATA_PATH)
