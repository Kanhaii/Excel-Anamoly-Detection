"""
Excel file loader and data import utilities.
"""

import pandas as pd
from pathlib import Path
from typing import Optional, Tuple
from utils.logging_config import get_logger

logger = get_logger("loader")

class ExcelLoader:
    """Load and import Excel files."""
    
    def __init__(self):
        """Initialize the loader."""
        pass
    
    def load_excel(self, file_path: Path, sheet_name: str = 0) -> Optional[pd.DataFrame]:
        """
        Load Excel file into a DataFrame.
        
        Args:
            file_path: Path to Excel file
            sheet_name: Sheet name or index (default 0)
        
        Returns:
            DataFrame or None if load fails
        """
        try:
            # Check file exists
            if not file_path.exists():
                logger.error(f"File not found: {file_path}")
                return None
            
            # Check file extension
            if not file_path.suffix.lower() in ['.xlsx', '.xls']:
                logger.error(f"Invalid file format: {file_path.suffix}")
                return None
            
            # Load Excel file
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            logger.info(f"Successfully loaded Excel file: {file_path} ({len(df)} rows, {len(df.columns)} columns)")
            
            return df
        
        except Exception as e:
            logger.error(f"Error loading Excel file: {str(e)}")
            return None
    
    def load_from_bytes(self, file_bytes: bytes) -> Optional[pd.DataFrame]:
        """
        Load Excel from bytes (e.g., uploaded file).
        
        Args:
            file_bytes: File contents as bytes
        
        Returns:
            DataFrame or None if load fails
        """
        try:
            from io import BytesIO
            df = pd.read_excel(BytesIO(file_bytes))
            logger.info(f"Successfully loaded Excel from bytes ({len(df)} rows, {len(df.columns)} columns)")
            return df
        
        except Exception as e:
            logger.error(f"Error loading Excel from bytes: {str(e)}")
            return None
    
    def get_sheet_names(self, file_path: Path) -> list:
        """
        Get available sheet names from Excel file.
        
        Args:
            file_path: Path to Excel file
        
        Returns:
            List of sheet names
        """
        try:
            xls = pd.ExcelFile(file_path)
            return xls.sheet_names
        except Exception as e:
            logger.error(f"Error reading sheet names: {str(e)}")
            return []
    
    def get_sheet_names_from_bytes(self, file_bytes: bytes) -> list:
        """
        Get available sheet names from uploaded file bytes.
        
        Args:
            file_bytes: File contents as bytes
        
        Returns:
            List of sheet names
        """
        try:
            from io import BytesIO
            xls = pd.ExcelFile(BytesIO(file_bytes))
            return xls.sheet_names
        except Exception as e:
            logger.error(f"Error reading sheet names from bytes: {str(e)}")
            return []
