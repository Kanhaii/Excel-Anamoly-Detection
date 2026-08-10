"""
Data cleaning and preprocessing utilities.
"""

import pandas as pd
import numpy as np
from typing import Optional
from utils.logging_config import get_logger

logger = get_logger("cleaner")

class DataCleaner:
    """Clean and preprocess data."""
    
    @staticmethod
    def clean_data(df: pd.DataFrame, date_column: Optional[str] = None) -> pd.DataFrame:
        """
        Apply cleaning operations to a DataFrame.
        
        Args:
            df: DataFrame to clean
            date_column: Name of date column if known
        
        Returns:
            Cleaned DataFrame
        """
        df = df.copy()
        
        # Remove completely empty rows
        df = df.dropna(how='all')
        
        # Remove completely empty columns
        df = df.dropna(axis=1, how='all')
        
        # Parse date column if specified
        if date_column and date_column in df.columns:
            try:
                df[date_column] = pd.to_datetime(df[date_column])
                logger.info(f"Parsed date column: {date_column}")
            except Exception as e:
                logger.warning(f"Could not parse date column {date_column}: {str(e)}")
        
        # Convert numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            # Replace infinite values with NaN
            df[col] = df[col].replace([np.inf, -np.inf], np.nan)
        
        logger.info(f"Data cleaning complete: {len(df)} rows, {len(df.columns)} columns")
        
        return df
    
    @staticmethod
    def sort_by_date(df: pd.DataFrame, date_column: str) -> pd.DataFrame:
        """
        Sort DataFrame by date column.
        
        Args:
            df: DataFrame to sort
            date_column: Name of date column
        
        Returns:
            Sorted DataFrame
        """
        if date_column not in df.columns:
            logger.warning(f"Date column {date_column} not found")
            return df
        
        df = df.copy()
        df = df.sort_values(by=date_column, ascending=True)
        logger.info(f"Sorted data by {date_column}")
        
        return df
    
    @staticmethod
    def handle_missing_values(df: pd.DataFrame, method: str = "forward_fill") -> pd.DataFrame:
        """
        Handle missing values in numeric columns.
        
        Args:
            df: DataFrame with missing values
            method: Method to use ('forward_fill', 'backward_fill', 'interpolate', 'drop')
        
        Returns:
            DataFrame with missing values handled
        """
        df = df.copy()
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            if df[col].isnull().any():
                if method == "forward_fill":
                    df[col] = df[col].fillna(method='ffill')
                elif method == "backward_fill":
                    df[col] = df[col].fillna(method='bfill')
                elif method == "interpolate":
                    df[col] = df[col].interpolate(method='linear', limit_direction='both')
                elif method == "drop":
                    df = df.dropna(subset=[col])
        
        logger.info(f"Missing values handled using method: {method}")
        
        return df
    
    @staticmethod
    def remove_outliers_iqr(df: pd.DataFrame, column: str, multiplier: float = 1.5) -> pd.DataFrame:
        """
        Remove outliers using Interquartile Range (IQR) method.
        
        Args:
            df: DataFrame
            column: Column name to check
            multiplier: IQR multiplier (default 1.5)
        
        Returns:
            DataFrame with outliers removed
        """
        if column not in df.columns:
            return df
        
        df = df.copy()
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - multiplier * IQR
        upper_bound = Q3 + multiplier * IQR
        
        initial_len = len(df)
        df = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
        removed = initial_len - len(df)
        
        logger.info(f"Removed {removed} outliers from {column} using IQR method")
        
        return df
    
    @staticmethod
    def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize column names (lowercase, strip whitespace).
        
        Args:
            df: DataFrame
        
        Returns:
            DataFrame with normalized column names
        """
        df = df.copy()
        df.columns = [col.lower().strip() for col in df.columns]
        return df
