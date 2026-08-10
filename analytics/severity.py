"""
Anomaly severity classification.
"""

from enum import Enum
from typing import Optional
from dataclasses import dataclass
from config.settings import SEVERITY_THRESHOLDS

class Severity(Enum):
    """Severity levels for anomalies."""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

@dataclass
class SeverityClassification:
    """Result of severity classification."""
    severity: Severity
    threshold_used: float
    reasoning: str

class SeverityClassifier:
    """Classify anomaly severity."""
    
    @staticmethod
    def classify(percentage_change: Optional[float],
                 z_score: Optional[float],
                 confidence: float,
                 is_positive: bool = None) -> SeverityClassification:
        """
        Classify severity of an anomaly.
        
        Args:
            percentage_change: Percentage change value
            z_score: Z-score value
            confidence: Confidence score (0-1)
            is_positive: Whether change is positive (for context)
        
        Returns:
            SeverityClassification object
        """
        # Use absolute values
        pct = abs(percentage_change) if percentage_change else 0
        z = abs(z_score) if z_score else 0
        
        # Composite score: weighted combination of signals
        # 40% weight to percentage change, 40% to z-score, 20% to confidence
        composite = (pct / 100.0 * 0.4) + (z / 5.0 * 0.4) + (confidence * 0.2)
        
        # Classify based on thresholds
        critical_threshold = SEVERITY_THRESHOLDS["CRITICAL"] / 100.0
        warning_threshold = SEVERITY_THRESHOLDS["WARNING"] / 100.0
        
        if composite >= critical_threshold / 100.0 or pct >= SEVERITY_THRESHOLDS["CRITICAL"]:
            return SeverityClassification(
                severity=Severity.CRITICAL,
                threshold_used=SEVERITY_THRESHOLDS["CRITICAL"],
                reasoning=f"Large change ({pct:.1f}%) with high z-score ({z:.2f})"
            )
        elif composite >= warning_threshold / 100.0 or pct >= SEVERITY_THRESHOLDS["WARNING"]:
            return SeverityClassification(
                severity=Severity.WARNING,
                threshold_used=SEVERITY_THRESHOLDS["WARNING"],
                reasoning=f"Moderate change ({pct:.1f}%) detected"
            )
        else:
            return SeverityClassification(
                severity=Severity.INFO,
                threshold_used=SEVERITY_THRESHOLDS["INFO"],
                reasoning=f"Minor change ({pct:.1f}%) detected"
            )
