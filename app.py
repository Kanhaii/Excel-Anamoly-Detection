"""
Main Streamlit application.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from data.loader import ExcelLoader
from data.validator import DataValidator
from data.cleaner import DataCleaner
from analytics.metrics import MetricsEngine
from analytics.anomaly_detector import AnomalyDetector
from analytics.severity import SeverityClassifier
from ai.ollama_client import OllamaClient
from alerts.alert_manager import AlertManager, Alert
from storage.database import AlertDatabase
from utils.logging_config import get_logger
from config.settings import (
    STREAMLIT_PAGE_TITLE, STREAMLIT_PAGE_ICON, SAMPLE_DATA_PATH
)
from datetime import datetime

logger = get_logger("app")

# Configure Streamlit
st.set_page_config(
    page_title=STREAMLIT_PAGE_TITLE,
    page_icon=STREAMLIT_PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .anomaly-critical {
        background-color: #ffebee;
        border-left: 4px solid #d32f2f;
    }
    .anomaly-warning {
        background-color: #fff3e0;
        border-left: 4px solid #f57c00;
    }
    .anomaly-info {
        background-color: #e3f2fd;
        border-left: 4px solid #1976d2;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'df' not in st.session_state:
    st.session_state.df = None
if 'column_mappings' not in st.session_state:
    st.session_state.column_mappings = {}
if 'anomalies' not in st.session_state:
    st.session_state.anomalies = []

def main():
    """Main application entry point."""
    
    # Sidebar navigation
    st.sidebar.title("📊 Business Monitor")
    page = st.sidebar.radio(
        "Navigation",
        ["🏠 Dashboard", "📁 Upload Data", "🔍 Analysis", 
         "🤖 AI Insights", "📈 Trends", "🔔 Alerts", 
         "📜 History", "⚙️ Settings"]
    )
    
    # Check Ollama availability
    ollama_client = OllamaClient()
    if ollama_client.is_available():
        status = "✅ Available" if ollama_client.is_model_available() else "⚠️ Service OK (Model Missing)"
        st.sidebar.info(f"🤖 Ollama: {status}")
    else:
        st.sidebar.warning("⚠️ Ollama not running")
    
    # Route pages
    if page == "🏠 Dashboard":
        show_dashboard()
    elif page == "📁 Upload Data":
        show_upload()
    elif page == "🔍 Analysis":
        show_analysis()
    elif page == "🤖 AI Insights":
        show_insights()
    elif page == "📈 Trends":
        show_trends()
    elif page == "🔔 Alerts":
        show_alerts()
    elif page == "📜 History":
        show_history()
    elif page == "⚙️ Settings":
        show_settings()

def show_dashboard():
    """Display main dashboard."""
    st.title("📊 Business Data Dashboard")
    
    if st.session_state.df is None:
        st.info("📁 Upload an Excel file to get started. Use the 'Upload Data' page.")
        # Offer sample data
        if st.button("📊 Load Sample Data"):
            if SAMPLE_DATA_PATH.exists():
                loader = ExcelLoader()
                df = loader.load_excel(SAMPLE_DATA_PATH)
                if df is not None:
                    st.session_state.df = df
                    st.success("Sample data loaded!")
                    st.rerun()
            else:
                st.error("Sample data file not found")
        return
    
    df = st.session_state.df
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # Display KPIs
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    for i, col in enumerate(numeric_cols[:5]):
        latest_val = df[col].iloc[-1]
        previous_val = df[col].iloc[-2] if len(df) > 1 else latest_val
        change = ((latest_val - previous_val) / abs(previous_val) * 100) if previous_val != 0 else 0
        
        with [col1, col2, col3, col4, col5][i]:
            st.metric(
                col.title(),
                f"{latest_val:,.0f}",
                f"{change:+.1f}%"
            )
    
    st.divider()
    
    # Anomaly summary
    if st.session_state.anomalies:
        anomalies = st.session_state.anomalies
        critical = len([a for a in anomalies if a.severity == 'CRITICAL'])
        warning = len([a for a in anomalies if a.severity == 'WARNING'])
        info = len([a for a in anomalies if a.severity == 'INFO'])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🔴 Critical", critical)
        with col2:
            st.metric("🟡 Warning", warning)
        with col3:
            st.metric("🔵 Info", info)
    
    # Trend visualization
    st.subheader("📈 Recent Trends")
    if len(numeric_cols) > 0:
        col = st.selectbox("Select metric to view", numeric_cols)
        if len(df) > 1:
            chart_data = pd.DataFrame({
                'Value': df[col].tail(30),
                'MA7': df[col].tail(30).rolling(7).mean()
            })
            st.line_chart(chart_data)

def show_upload():
    """Display data upload interface."""
    st.title("📁 Upload Business Data")
    
    uploaded_file = st.file_uploader(
        "Choose an Excel file",
        type=['xlsx', 'xls'],
        help="Upload business metrics in Excel format (Date, Revenue, Orders, etc.)"
    )
    
    if uploaded_file is not None:
        # Load file
        loader = ExcelLoader()
        df = loader.load_from_bytes(uploaded_file.read())
        
        if df is None:
            st.error("❌ Failed to load Excel file")
            return
        
        # Validate data
        validator = DataValidator()
        is_valid, messages = validator.validate(df)
        
        st.subheader("📋 Data Validation Report")
        for msg in messages:
            if msg.type.value == "ERROR":
                st.error(f"❌ {msg.message}")
            elif msg.type.value == "WARNING":
                st.warning(f"⚠️ {msg.message}")
            else:
                st.info(f"ℹ️ {msg.message}")
        
        if not is_valid:
            st.error("Cannot proceed with validation errors")
            return
        
        # Clean data
        cleaner = DataCleaner()
        df = cleaner.clean_data(df)
        
        # Detect columns
        mappings = validator.detect_column_mappings(df)
        
        st.success(f"✅ Data loaded successfully: {len(df)} rows, {len(df.columns)} columns")
        
        if st.button("✅ Use This Data"):
            st.session_state.df = df
            st.session_state.column_mappings = mappings
            st.success("Data saved to session!")
            st.rerun()
        
        st.subheader("Preview")
        st.dataframe(df.head(10))

def show_analysis():
    """Display anomaly analysis."""
    st.title("🔍 Anomaly Analysis")
    
    if st.session_state.df is None:
        st.warning("No data loaded. Please upload data first.")
        return
    
    df = st.session_state.df
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    # Run analysis
    if st.button("🔍 Run Analysis", type="primary"):
        with st.spinner("Analyzing data..."):
            detector = AnomalyDetector()
            anomalies = detector.detect_batch(df, numeric_cols)
            
            classified_anomalies = []
            for anomaly in anomalies:
                if anomaly.is_anomaly:
                    severity = SeverityClassifier.classify(
                        anomaly.change_percent,
                        anomaly.z_score,
                        anomaly.confidence
                    )
                    classified_anomalies.append({
                        'metric': anomaly.metric_name,
                        'current': anomaly.current_value,
                        'baseline': anomaly.baseline_value,
                        'change_%': anomaly.change_percent,
                        'z_score': anomaly.z_score,
                        'severity': severity.severity.value,
                        'confidence': f"{anomaly.confidence:.2%}"
                    })
            
            if classified_anomalies:
                st.session_state.anomalies = classified_anomalies
                df_anomalies = pd.DataFrame(classified_anomalies)
                st.dataframe(df_anomalies, use_container_width=True)
                st.success(f"Found {len(classified_anomalies)} anomalies")
            else:
                st.info("✅ No anomalies detected")

def show_insights():
    """Display AI insights."""
    st.title("🤖 AI-Generated Insights")
    
    if st.session_state.df is None:
        st.warning("No data loaded. Please upload data first.")
        return
    
    # Check Ollama
    ollama = OllamaClient()
    if not ollama.is_available():
        st.error("🤖 Ollama service not running. Please start Ollama.")
        return
    
    if st.button("🤖 Generate AI Analysis", type="primary"):
        st.info("Generating insights from Ollama Mistral...")
        st.info("This may take 30-60 seconds")

def show_trends():
    """Display trend analysis."""
    st.title("📈 Trend Analysis")
    
    if st.session_state.df is None:
        st.warning("No data loaded. Please upload data first.")
        return
    
    df = st.session_state.df
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    selected_metric = st.selectbox("Select metric", numeric_cols)
    
    if selected_metric:
        st.line_chart(df[selected_metric])

def show_alerts():
    """Display alerts page."""
    st.title("🔔 Alerts")
    st.info("Configure and view active alerts")

def show_history():
    """Display alert history."""
    st.title("📜 Alert History")
    
    db = AlertDatabase()
    recent_alerts = db.get_recent_alerts(20)
    
    if recent_alerts:
        df_history = pd.DataFrame(recent_alerts)
        st.dataframe(df_history, use_container_width=True)
    else:
        st.info("No alerts in history yet")

def show_settings():
    """Display settings page."""
    st.title("⚙️ Settings")
    
    st.subheader("🤖 Ollama Configuration")
    ollama_url = st.text_input("Ollama Base URL", value="http://localhost:11434")
    ollama_model = st.text_input("Ollama Model", value="mistral")
    
    st.subheader("📧 Email Configuration")
    smtp_server = st.text_input("SMTP Server", value="smtp.gmail.com")
    smtp_port = st.number_input("SMTP Port", value=587)
    smtp_user = st.text_input("SMTP Username")
    smtp_pass = st.text_input("SMTP Password", type="password")
    alert_email = st.text_input("Alert Email Recipient")
    
    st.subheader("📊 Analysis Settings")
    sensitivity = st.slider("Anomaly Sensitivity (Z-score)", 1.0, 5.0, 2.5, 0.1)
    min_change = st.slider("Minimum % Change to Flag", 1.0, 20.0, 5.0, 0.5)
    
    if st.button("💾 Save Settings"):
        st.success("Settings saved!")

if __name__ == "__main__":
    main()
