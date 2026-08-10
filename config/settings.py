"""
Configuration and settings management for the application.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project root
PROJECT_ROOT = Path(__file__).parent.parent

# Ollama Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")
OLLAMA_TIMEOUT = 120  # seconds

# Email Configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
ALERT_EMAIL = os.getenv("ALERT_EMAIL", "")
SMTP_USE_TLS = True

# Anomaly Detection Settings
ANOMALY_SENSITIVITY = float(os.getenv("ANOMALY_SENSITIVITY", "2.5"))  # Z-score threshold
MIN_PERCENTAGE_CHANGE = float(os.getenv("MIN_PERCENTAGE_CHANGE", "5.0"))  # Minimum % change to flag
MIN_ABSOLUTE_CHANGE = 100  # Minimum absolute change (currency-dependent)

# Moving Average Windows (days)
MA_SHORT = 7
MA_MEDIUM = 14
MA_LONG = 30

# Severity Thresholds (percentage change)
SEVERITY_THRESHOLDS = {
    "INFO": 5.0,      # >= 5%
    "WARNING": 15.0,  # >= 15%
    "CRITICAL": 25.0  # >= 25%
}

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Data Storage
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)
UPLOADS_DIR = DATA_DIR / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)

# Database
DB_PATH = DATA_DIR / "alerts.db"

# Alert History
ALERT_HISTORY_CSV = DATA_DIR / "alerts_history.csv"
ALERT_RETENTION_DAYS = int(os.getenv("ALERT_HISTORY_RETENTION_DAYS", "90"))

# Sample Data
SAMPLE_DATA_PATH = PROJECT_ROOT / "sample_data" / "business_metrics.xlsx"

# Column Mapping (flexible column name detection)
COLUMN_ALIASES = {
    "revenue": ["revenue", "sales", "total_sales", "net_revenue", "gross_revenue"],
    "orders": ["orders", "order_count", "total_orders", "transactions"],
    "traffic": ["traffic", "visits", "sessions", "page_views", "unique_visitors"],
    "conversion_rate": ["conversion_rate", "conversion", "ctr", "conversion_percent"],
    "cost": ["cost", "total_cost", "operating_cost", "cogs"],
    "refunds": ["refunds", "returns", "refund_amount"],
    "profit": ["profit", "net_profit", "net_income", "earnings"],
    "customers": ["customers", "customer_count", "unique_customers"],
    "date": ["date", "day", "transaction_date", "order_date"]
}

# Streamlit Configuration
STREAMLIT_PAGE_TITLE = "Business Data Monitor"
STREAMLIT_PAGE_ICON = "📊"

# AI Prompt Templates
AI_PROMPT_TEMPLATE = """You are a senior business data analyst.

You are given verified analytical results calculated by a Python analytics engine.

Your task is to interpret these results for a business stakeholder in clear, actionable language.

CRITICAL RULES:
- Do NOT recalculate or invent numbers
- Do NOT introduce metrics not provided
- Do NOT claim causation unless supported by data
- Distinguish between: Observed facts, Possible explanations, Recommended investigations
- Use concise business language
- Format response as valid JSON with the following structure:
{{
    "executive_summary": "2-3 sentence business impact statement",
    "key_changes": ["change 1", "change 2"],
    "business_implications": ["implication 1"],
    "recommended_actions": ["action 1", "action 2"]
}}

Analytical Results:
{analysis_data}

Provide your analysis as JSON only, no markdown formatting."""
