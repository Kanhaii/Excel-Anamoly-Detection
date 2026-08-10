"""
Utility helper functions.
"""

import pandas as pd
import numpy as np
from typing import Optional, Any, Dict, List
from datetime import datetime

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, returning default if denominator is zero.
    
    Args:
        numerator: Dividend
        denominator: Divisor
        default: Default value if division by zero
    
    Returns:
        Result of division or default value
    """
    try:
        if denominator == 0 or pd.isna(denominator):
            return default
        result = numerator / denominator
        return default if pd.isna(result) or np.isinf(result) else result
    except (ZeroDivisionError, TypeError):
        return default

def calculate_percentage_change(current: float, previous: float) -> Optional[float]:
    """
    Calculate percentage change from previous to current value.
    
    Args:
        current: Current value
        previous: Previous value
    
    Returns:
        Percentage change or None if calculation not possible
    """
    if pd.isna(current) or pd.isna(previous) or previous == 0:
        return None
    
    pct_change = ((current - previous) / abs(previous)) * 100
    return None if pd.isna(pct_change) or np.isinf(pct_change) else pct_change

def calculate_z_score(value: float, mean: float, std: float) -> Optional[float]:
    """
    Calculate z-score for a value.
    
    Args:
        value: The value
        mean: Mean of distribution
        std: Standard deviation
    
    Returns:
        Z-score or None if calculation not possible
    """
    if pd.isna(value) or pd.isna(mean) or pd.isna(std) or std == 0:
        return None
    
    z = (value - mean) / std
    return None if pd.isna(z) or np.isinf(z) else z

def format_number(value: float, decimals: int = 2, prefix: str = "") -> str:
    """
    Format a number as a string with thousand separators.
    
    Args:
        value: Number to format
        decimals: Decimal places
        prefix: Prefix (e.g., "$")
    
    Returns:
        Formatted string
    """
    if pd.isna(value):
        return "N/A"
    return f"{prefix}{value:,.{decimals}f}"

def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Format a number as a percentage string.
    
    Args:
        value: Number (not yet multiplied by 100)
        decimals: Decimal places
    
    Returns:
        Formatted percentage string
    """
    if pd.isna(value):
        return "N/A"
    return f"{value:.{decimals}f}%"

def get_direction_indicator(value: float) -> str:
    """
    Get an emoji indicator for direction (up/down/neutral).
    
    Args:
        value: The value (positive = up, negative = down)
    
    Returns:
        Direction indicator emoji
    """
    if pd.isna(value):
        return "➡️"
    if value > 0:
        return "📈"
    elif value < 0:
        return "📉"
    else:
        return "➡️"

def truncate_string(text: str, max_length: int = 100) -> str:
    """
    Truncate string to max length with ellipsis.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
    
    Returns:
        Truncated text
    """
    if len(text) > max_length:
        return text[:max_length-3] + "..."
    return text

def convert_to_native_python(obj: Any) -> Any:
    """
    Convert numpy/pandas types to native Python types for JSON serialization.
    
    Args:
        obj: Object to convert
    
    Returns:
        Converted object
    """
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.Series):
        return obj.to_dict()
    elif isinstance(obj, pd.DataFrame):
        return obj.to_dict('records')
    elif isinstance(obj, (datetime, pd.Timestamp)):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: convert_to_native_python(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_to_native_python(item) for item in obj]
    return obj
