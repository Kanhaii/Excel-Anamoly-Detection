"""
Trend analysis and time-series calculations.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from utils.logging_config import get_logger

logger = get_logger("trends")

@dataclass
class TrendData:
    """Container for trend analysis."""
    metric_name: str
    dates: List
    values: List[float]
    moving_avg_7: List[float]
    moving_avg_30: List[float]
    trend_label: str
    direction: str  # UP, DOWN, STABLE

class TrendsEngine:
    """Analyze trends in business metrics."""
    
    def __init__(self):
        """Initialize trends engine."""
        pass
    
    def get_trend_data(self, df: pd.DataFrame, date_col: str, metric_col: str, 
                       metric_name: str) -> TrendData:
        """
        Extract trend data for visualization.
        
        Args:
            df: DataFrame with time series data
            date_col: Column name for dates
            metric_col: Column name for metric
            metric_name: Display name for metric
        
        Returns:
            TrendData object
        """
        if date_col not in df.columns or metric_col not in df.columns:
            return None
        
        # Sort by date
        df_sorted = df.sort_values(date_col)
        
        dates = df_sorted[date_col].tolist()
        values = df_sorted[metric_col].fillna(method='ffill').tolist()
        
        # Calculate moving averages
        ma_7 = pd.Series(values).rolling(window=7, min_periods=1).mean().tolist()
        ma_30 = pd.Series(values).rolling(window=30, min_periods=1).mean().tolist()
        
        # Determine trend
        trend_label = self._describe_trend(pd.Series(values))
        direction = self._get_direction(pd.Series(values))
        
        return TrendData(
            metric_name=metric_name,
            dates=dates,
            values=values,
            moving_avg_7=ma_7,
            moving_avg_30=ma_30,
            trend_label=trend_label,
            direction=direction
        )
    
    def _describe_trend(self, series: pd.Series) -> str:
        """
        Generate a human-readable trend description.
        
        Args:
            series: Time series
        
        Returns:
            Trend description
        """
        if len(series) < 2:
            return "Insufficient Data"
        
        recent = series.tail(7).mean()
        historical = series.head(-7).mean() if len(series) > 7 else series.mean()
        
        if pd.isna(recent) or pd.isna(historical):
            return "Insufficient Data"
        
        if historical == 0:
            return "Baseline Zero"
        
        change_pct = ((recent - historical) / abs(historical)) * 100
        
        if change_pct > 20:
            return "Strong Upward Trend"
        elif change_pct > 5:
            return "Moderate Upward Trend"
        elif change_pct < -20:
            return "Strong Downward Trend"
        elif change_pct < -5:
            return "Moderate Downward Trend"
        else:
            return "Stable Trend"
    
    def _get_direction(self, series: pd.Series) -> str:
        """
        Get simple direction indicator.
        
        Args:
            series: Time series
        
        Returns:
            UP, DOWN, or STABLE
        """
        if len(series) < 2:
            return "STABLE"
        
        current = series.iloc[-1]
        previous = series.iloc[-2]
        
        if pd.isna(current) or pd.isna(previous):
            return "STABLE"
        
        if current > previous:
            return "UP"
        elif current < previous:
            return "DOWN"
        else:
            return "STABLE"
    
    def detect_seasonality(self, series: pd.Series, window: int = 30) -> bool:
        """
        Simple seasonality detection using autocorrelation.
        
        Args:
            series: Time series data
            window: Window size to check
        
        Returns:
            True if seasonality detected
        """
        if len(series) < window * 2:
            return False
        
        try:
            # Calculate autocorrelation at lag=window
            autocorr = series.autocorr(lag=window)
            return abs(autocorr) > 0.3  # Threshold for seasonality
        except:
            return False
