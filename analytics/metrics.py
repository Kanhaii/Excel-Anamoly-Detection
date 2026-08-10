"""
Metric calculation and analysis engine.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, List
from dataclasses import dataclass
from utils.helpers import safe_divide, calculate_percentage_change, calculate_z_score
from utils.logging_config import get_logger
from config.settings import MA_SHORT, MA_MEDIUM, MA_LONG

logger = get_logger("metrics")

@dataclass
class MetricAnalysis:
    """Container for metric analysis results."""
    metric_name: str
    current_value: float
    previous_value: Optional[float]
    absolute_change: Optional[float]
    percentage_change: Optional[float]
    ma_short: Optional[float]  # 7-day
    ma_medium: Optional[float]  # 14-day
    ma_long: Optional[float]  # 30-day
    rolling_std: Optional[float]
    z_score: Optional[float]
    trend_direction: str

class MetricsEngine:
    """Calculate and analyze business metrics."""
    
    def __init__(self):
        """Initialize metrics engine."""
        pass
    
    def analyze_metric(self, series: pd.Series, column_name: str) -> MetricAnalysis:
        """
        Perform comprehensive analysis on a single metric.
        
        Args:
            series: Pandas Series of metric values
            column_name: Name of the metric
        
        Returns:
            MetricAnalysis object with all calculated values
        """
        # Remove NaN values
        series = series.dropna()
        
        if len(series) < 2:
            return MetricAnalysis(
                metric_name=column_name,
                current_value=series.iloc[-1] if len(series) > 0 else 0,
                previous_value=None,
                absolute_change=None,
                percentage_change=None,
                ma_short=None,
                ma_medium=None,
                ma_long=None,
                rolling_std=None,
                z_score=None,
                trend_direction="INSUFFICIENT_DATA"
            )
        
        current = series.iloc[-1]
        previous = series.iloc[-2]
        
        # Calculate changes
        abs_change = current - previous
        pct_change = calculate_percentage_change(current, previous)
        
        # Calculate moving averages
        ma_short = series.tail(MA_SHORT).mean() if len(series) >= MA_SHORT else series.mean()
        ma_medium = series.tail(MA_MEDIUM).mean() if len(series) >= MA_MEDIUM else series.mean()
        ma_long = series.tail(MA_LONG).mean() if len(series) >= MA_LONG else series.mean()
        
        # Calculate rolling statistics
        rolling_std = series.tail(max(MA_SHORT, 7)).std()
        
        # Calculate z-score against recent baseline
        rolling_mean = series.tail(max(MA_SHORT, 7)).mean()
        z_score = calculate_z_score(current, rolling_mean, rolling_std)
        
        # Determine trend
        trend = self._determine_trend(series)
        
        return MetricAnalysis(
            metric_name=column_name,
            current_value=current,
            previous_value=previous,
            absolute_change=abs_change,
            percentage_change=pct_change,
            ma_short=ma_short,
            ma_medium=ma_medium,
            ma_long=ma_long,
            rolling_std=rolling_std,
            z_score=z_score,
            trend_direction=trend
        )
    
    def _determine_trend(self, series: pd.Series, window: int = 14) -> str:
        """
        Determine trend direction over a window.
        
        Args:
            series: Time series data
            window: Window size for trend calculation
        
        Returns:
            Trend direction string
        """
        if len(series) < window:
            return "INSUFFICIENT_DATA"
        
        recent = series.tail(window)
        older = series.iloc[-2*window:-window] if len(series) >= 2*window else series.head(window)
        
        recent_mean = recent.mean()
        older_mean = older.mean()
        
        if pd.isna(recent_mean) or pd.isna(older_mean) or older_mean == 0:
            return "STABLE"
        
        pct_trend = ((recent_mean - older_mean) / abs(older_mean)) * 100
        
        if pct_trend > 15:
            return "STRONG_INCREASE"
        elif pct_trend > 5:
            return "MODERATE_INCREASE"
        elif pct_trend < -15:
            return "STRONG_DECREASE"
        elif pct_trend < -5:
            return "MODERATE_DECREASE"
        else:
            return "STABLE"
    
    def calculate_derived_metrics(self, df: pd.DataFrame, column_mappings: Dict[str, str]) -> Dict[str, float]:
        """
        Calculate derived metrics (AOV, profit margin, etc.).
        
        Args:
            df: DataFrame with data
            column_mappings: Mapping of metric names to column names
        
        Returns:
            Dictionary of derived metric names to values
        """
        derived = {}
        
        # Average Order Value = Revenue / Orders
        if "revenue" in column_mappings and "orders" in column_mappings:
            rev_col = column_mappings["revenue"]
            ord_col = column_mappings["orders"]
            if rev_col in df.columns and ord_col in df.columns:
                latest_rev = df[rev_col].iloc[-1]
                latest_orders = df[ord_col].iloc[-1]
                aov = safe_divide(latest_rev, latest_orders)
                if aov > 0:
                    derived["average_order_value"] = aov
        
        # Profit Margin = Profit / Revenue
        if "profit" in column_mappings and "revenue" in column_mappings:
            prof_col = column_mappings["profit"]
            rev_col = column_mappings["revenue"]
            if prof_col in df.columns and rev_col in df.columns:
                latest_profit = df[prof_col].iloc[-1]
                latest_rev = df[rev_col].iloc[-1]
                margin = safe_divide(latest_profit, latest_rev) * 100
                derived["profit_margin_percent"] = margin
        
        # Conversion Rate = Orders / Traffic
        if "orders" in column_mappings and "traffic" in column_mappings:
            ord_col = column_mappings["orders"]
            traf_col = column_mappings["traffic"]
            if ord_col in df.columns and traf_col in df.columns:
                latest_orders = df[ord_col].iloc[-1]
                latest_traffic = df[traf_col].iloc[-1]
                conv_rate = safe_divide(latest_orders, latest_traffic) * 100
                if conv_rate >= 0:
                    derived["conversion_rate_percent"] = conv_rate
        
        # Refund Rate = Refunds / Orders
        if "refunds" in column_mappings and "orders" in column_mappings:
            ref_col = column_mappings["refunds"]
            ord_col = column_mappings["orders"]
            if ref_col in df.columns and ord_col in df.columns:
                latest_refunds = df[ref_col].iloc[-1]
                latest_orders = df[ord_col].iloc[-1]
                refund_rate = safe_divide(latest_refunds, latest_orders) * 100
                if refund_rate >= 0:
                    derived["refund_rate_percent"] = refund_rate
        
        return derived
