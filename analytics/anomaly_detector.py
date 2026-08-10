"""
Anomaly detection engine with multiple methods.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
from utils.helpers import calculate_percentage_change, calculate_z_score
from utils.logging_config import get_logger
from config.settings import (
    ANOMALY_SENSITIVITY,
    MIN_PERCENTAGE_CHANGE,
    MIN_ABSOLUTE_CHANGE,
    MA_SHORT
)

logger = get_logger("anomaly_detector")

class AnomalyMethod(Enum):
    """Anomaly detection methods."""
    PERCENTAGE_CHANGE = "percentage_change"
    Z_SCORE = "z_score"
    ROLLING_BASELINE = "rolling_baseline"

@dataclass
class Anomaly:
    """Container for anomaly detection result."""
    metric_name: str
    current_value: float
    baseline_value: float
    change_absolute: Optional[float]
    change_percent: Optional[float]
    z_score: Optional[float]
    method_detected: str  # Which method(s) detected it
    is_anomaly: bool
    confidence: float  # 0.0 to 1.0

class AnomalyDetector:
    """Detect anomalies in business metrics."""
    
    def __init__(self, sensitivity: float = ANOMALY_SENSITIVITY,
                 min_pct_change: float = MIN_PERCENTAGE_CHANGE):
        """
        Initialize detector.
        
        Args:
            sensitivity: Z-score threshold (default 2.5)
            min_pct_change: Minimum percentage change to flag (default 5%)
        """
        self.sensitivity = sensitivity
        self.min_pct_change = min_pct_change
    
    def detect(self, series: pd.Series, metric_name: str) -> Anomaly:
        """
        Detect anomaly in a single metric.
        
        Args:
            series: Time series of metric values
            metric_name: Name of metric
        
        Returns:
            Anomaly object
        """
        series = series.dropna()
        
        if len(series) < 2:
            return Anomaly(
                metric_name=metric_name,
                current_value=series.iloc[-1] if len(series) > 0 else 0,
                baseline_value=0,
                change_absolute=None,
                change_percent=None,
                z_score=None,
                method_detected="NONE",
                is_anomaly=False,
                confidence=0.0
            )
        
        current = series.iloc[-1]
        previous = series.iloc[-2]
        
        # Calculate changes
        abs_change = current - previous
        pct_change = calculate_percentage_change(current, previous)
        
        # Calculate baseline (recent average, excluding today)
        baseline = series.tail(MA_SHORT + 1)[:-1].mean()
        
        # Calculate z-score
        rolling_std = series.tail(max(MA_SHORT, 7)).std()
        z_score = calculate_z_score(current, baseline, rolling_std)
        
        # Apply anomaly detection methods
        is_anomaly, methods, confidence = self._apply_detection_methods(
            current, baseline, pct_change, z_score, abs_change
        )
        
        return Anomaly(
            metric_name=metric_name,
            current_value=current,
            baseline_value=baseline,
            change_absolute=abs_change,
            change_percent=pct_change,
            z_score=z_score,
            method_detected=methods,
            is_anomaly=is_anomaly,
            confidence=confidence
        )
    
    def _apply_detection_methods(self, current: float, baseline: float,
                                  pct_change: Optional[float],
                                  z_score: Optional[float],
                                  abs_change: float) -> tuple:
        """
        Apply multiple anomaly detection methods.
        
        Returns:
            (is_anomaly, methods_string, confidence_score)
        """
        methods_triggered = []
        confidence_scores = []
        
        # Method 1: Percentage Change Threshold
        if pct_change is not None and abs(pct_change) >= self.min_pct_change:
            methods_triggered.append(AnomalyMethod.PERCENTAGE_CHANGE.value)
            # Higher confidence with larger changes
            conf = min(abs(pct_change) / 50.0, 1.0)  # Max out at 50%
            confidence_scores.append(conf)
        
        # Method 2: Z-Score Threshold
        if z_score is not None and abs(z_score) >= self.sensitivity:
            methods_triggered.append(AnomalyMethod.Z_SCORE.value)
            # Higher confidence with higher z-scores
            conf = min(abs(z_score) / 5.0, 1.0)  # Max out at |5.0|
            confidence_scores.append(conf)
        
        # Method 3: Rolling Baseline Deviation
        if baseline > 0:
            baseline_pct = abs(current - baseline) / baseline * 100
            if baseline_pct >= self.min_pct_change * 1.5:  # Slightly higher threshold
                methods_triggered.append(AnomalyMethod.ROLLING_BASELINE.value)
                conf = min(baseline_pct / 75.0, 1.0)
                confidence_scores.append(conf)
        
        is_anomaly = len(methods_triggered) > 0
        avg_confidence = np.mean(confidence_scores) if confidence_scores else 0.0
        methods_str = ", ".join(methods_triggered) if methods_triggered else "NONE"
        
        return is_anomaly, methods_str, avg_confidence
    
    def detect_batch(self, df: pd.DataFrame, metric_columns: List[str]) -> List[Anomaly]:
        """
        Detect anomalies across multiple metrics.
        
        Args:
            df: DataFrame with data
            metric_columns: List of metric column names
        
        Returns:
            List of Anomaly objects
        """
        anomalies = []
        
        for col in metric_columns:
            if col in df.columns:
                anomaly = self.detect(df[col], col)
                anomalies.append(anomaly)
        
        return anomalies
