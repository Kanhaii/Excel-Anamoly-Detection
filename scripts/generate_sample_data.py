#!/usr/bin/env python
"""
Generate sample business metrics data with intentional anomalies.
Run this script to create sample_data/business_metrics.xlsx
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sample_data.generate_sample import save_sample_data
from config.settings import SAMPLE_DATA_PATH

if __name__ == "__main__":
    print("\n" + "="*60)
    print("SAMPLE DATA GENERATOR")
    print("="*60)
    
    save_sample_data(SAMPLE_DATA_PATH)
    
    print("\n" + "="*60)
    print("✅ SUCCESS!")
    print("="*60)
    print(f"Sample data saved to: {SAMPLE_DATA_PATH}")
    print("\nYou can now:")
    print("1. Start Streamlit: streamlit run app.py")
    print("2. Go to Upload Data page")
    print("3. Load Sample Data from dashboard")
    print("4. Run analysis to detect injected anomalies")
    print("\nInjected Anomalies:")
    print("  • Day ~200: Traffic spike (+35%), Conversion drop (-25%)")
    print("  • Day ~250: Revenue sharp drop (-30%)")
    print("  • Day ~300: Refund rate spike (2.5x)")
    print("  • Day ~330: Cost jump (+40%) with flat revenue")
    print()
