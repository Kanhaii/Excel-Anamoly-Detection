"""
Unit tests for analytics engine.
"""

import pytest
import pandas as pd
import numpy as np
from analytics.metrics import MetricsEngine
from analytics.anomaly_detector import AnomalyDetector
from analytics.severity import SeverityClassifier, Severity
from analytics.trends import TrendsEngine
from utils.helpers import (
    safe_divide, calculate_percentage_change, calculate_z_score,
    format_number, format_percentage
)

class TestHelpers:
    """Test helper functions."""
    
    def test_safe_divide(self):
        assert safe_divide(10, 2) == 5.0
        assert safe_divide(10, 0) == 0.0
        assert safe_divide(10, 0, default=1.0) == 1.0
        assert safe_divide(10, 2, default=999) == 5.0
    
    def test_calculate_percentage_change(self):
        assert calculate_percentage_change(100, 50) == 100.0  # +100%
        assert calculate_percentage_change(50, 100) == -50.0  # -50%
        assert calculate_percentage_change(100, 100) == 0.0
        assert calculate_percentage_change(100, 0) is None  # Division by zero
    
    def test_calculate_z_score(self):
        z = calculate_z_score(100, 50, 25)  # (100-50)/25 = 2.0
        assert z == 2.0
        
        z = calculate_z_score(100, 100, 0)  # std = 0, should be None
        assert z is None
    
    def test_format_number(self):
        assert format_number(1234.56) == "1,234.56"
        assert format_number(1000000) == "1,000,000.00"
        assert format_number(99.1, decimals=1) == "99.1"
    
    def test_format_percentage(self):
        assert format_percentage(5.5) == "5.5%"
        assert format_percentage(-10.25) == "-10.2%"

class TestMetricsEngine:
    """Test metrics calculation engine."""
    
    def test_analyze_metric_basic(self):
        values = pd.Series([100, 102, 105, 103, 108])
        engine = MetricsEngine()
        result = engine.analyze_metric(values, "test_metric")
        
        assert result.metric_name == "test_metric"
        assert result.current_value == 108
        assert result.previous_value == 103
        assert result.absolute_change == 5.0
        assert result.percentage_change is not None
    
    def test_analyze_metric_insufficient_data(self):
        values = pd.Series([100])
        engine = MetricsEngine()
        result = engine.analyze_metric(values, "test_metric")
        
        assert result.trend_direction == "INSUFFICIENT_DATA"
    
    def test_determine_trend(self):
        # Strong increase trend
        values = pd.Series(range(1, 31))
        engine = MetricsEngine()
        trend = engine._determine_trend(values)
        assert trend == "STRONG_INCREASE"
        
        # Strong decrease trend
        values = pd.Series(range(30, 0, -1))
        trend = engine._determine_trend(values)
        assert trend == "STRONG_DECREASE"
        
        # Stable
        values = pd.Series([100] * 30)
        trend = engine._determine_trend(values)
        assert trend == "STABLE"
    
    def test_calculate_derived_metrics(self):
        df = pd.DataFrame({
            'revenue': [1000, 1100, 1200],
            'orders': [10, 11, 12],
            'profit': [200, 220, 240]
        })
        
        engine = MetricsEngine()
        mappings = {'revenue': 'revenue', 'orders': 'orders', 'profit': 'profit'}
        derived = engine.calculate_derived_metrics(df, mappings)
        
        assert 'average_order_value' in derived
        assert 'profit_margin_percent' in derived
        assert derived['average_order_value'] == 100.0  # 1200 / 12

class TestAnomalyDetector:
    """Test anomaly detection."""
    
    def test_detect_percentage_change_anomaly(self):
        # Normal: 100, 101, 102, 103, 104, 105, 130 (24% increase)
        values = pd.Series([100, 101, 102, 103, 104, 105, 130])
        detector = AnomalyDetector(sensitivity=2.5, min_pct_change=5.0)
        result = detector.detect(values, "test_metric")
        
        assert result.is_anomaly is True
        assert "percentage_change" in result.method_detected
    
    def test_detect_z_score_anomaly(self):
        # Normal data with outlier
        values = pd.Series([100, 101, 99, 102, 100, 101, 200])  # Last value is outlier
        detector = AnomalyDetector(sensitivity=2.5, min_pct_change=5.0)
        result = detector.detect(values, "test_metric")
        
        assert result.is_anomaly is True
    
    def test_detect_no_anomaly(self):
        # Very stable data
        values = pd.Series([100, 100.5, 100.2, 100.1, 100.3, 100.2])
        detector = AnomalyDetector(sensitivity=2.5, min_pct_change=5.0)
        result = detector.detect(values, "test_metric")
        
        assert result.is_anomaly is False
    
    def test_detect_batch(self):
        df = pd.DataFrame({
            'metric_a': [100, 101, 102, 103, 104, 105, 130],
            'metric_b': [50, 51, 49, 50, 51, 50, 51]
        })
        
        detector = AnomalyDetector()
        anomalies = detector.detect_batch(df, ['metric_a', 'metric_b'])
        
        assert len(anomalies) == 2
        # metric_a should have anomaly, metric_b should not
        assert any(a.is_anomaly for a in anomalies)

class TestSeverityClassifier:
    """Test severity classification."""
    
    def test_critical_severity(self):
        result = SeverityClassifier.classify(
            percentage_change=-30.0,
            z_score=-3.5,
            confidence=0.9
        )
        assert result.severity == Severity.CRITICAL
    
    def test_warning_severity(self):
        result = SeverityClassifier.classify(
            percentage_change=-18.0,
            z_score=2.0,
            confidence=0.7
        )
        assert result.severity == Severity.WARNING
    
    def test_info_severity(self):
        result = SeverityClassifier.classify(
            percentage_change=3.0,
            z_score=0.5,
            confidence=0.3
        )
        assert result.severity == Severity.INFO

class TestDataValidator:
    """Test data validation."""
    
    def test_validate_empty_dataframe(self):
        from data.validator import DataValidator
        df = pd.DataFrame()
        validator = DataValidator()
        is_valid, messages = validator.validate(df)
        
        assert is_valid is False
        assert len(messages) > 0
    
    def test_validate_valid_dataframe(self):
        from data.validator import DataValidator
        df = pd.DataFrame({
            'Date': pd.date_range('2023-01-01', periods=30),
            'Revenue': np.random.randint(1000, 2000, 30),
            'Orders': np.random.randint(50, 200, 30)
        })
        
        validator = DataValidator()
        is_valid, messages = validator.validate(df)
        
        # Should be valid
        errors = [m for m in messages if m.type.value == "ERROR"]
        assert len(errors) == 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
