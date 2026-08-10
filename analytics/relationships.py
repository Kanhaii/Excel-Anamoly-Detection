"""
Cross-metric relationship and impact analysis.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from utils.logging_config import get_logger

logger = get_logger("relationships")

@dataclass
class MetricRelationship:
    """Result of cross-metric relationship analysis."""
    metric_a: str
    metric_b: str
    correlation: float  # -1 to 1
    change_a: float  # percentage
    change_b: float  # percentage
    relationship_type: str  # POSITIVE, NEGATIVE, INDEPENDENT
    business_insight: str

class RelationshipAnalyzer:
    """Analyze relationships between metrics."""
    
    def __init__(self):
        """Initialize analyzer."""
        pass
    
    def analyze_relationships(self, df: pd.DataFrame, metric_columns: List[str],
                              recent_changes: Dict[str, float]) -> List[MetricRelationship]:
        """
        Analyze relationships between metrics.
        
        Args:
            df: DataFrame with data
            metric_columns: List of metric columns to analyze
            recent_changes: Dict of metric name to percentage change
        
        Returns:
            List of MetricRelationship objects
        """
        relationships = []
        
        # Calculate correlation matrix
        numeric_df = df[metric_columns].select_dtypes(include=[np.number])
        correlation_matrix = numeric_df.corr()
        
        # Identify key anomalies (those with large changes)
        anomalies = [m for m, chg in recent_changes.items() if abs(chg) > 10]
        
        # For each anomaly, find related metrics
        for metric in anomalies:
            if metric not in correlation_matrix.columns:
                continue
            
            correlations = correlation_matrix[metric].sort_values(ascending=False)
            
            for related_metric, corr_value in correlations.items():
                if related_metric == metric or abs(corr_value) < 0.3:  # Weak correlation
                    continue
                
                if related_metric not in recent_changes:
                    continue
                
                change_a = recent_changes[metric]
                change_b = recent_changes[related_metric]
                
                relationship = self._classify_relationship(
                    metric, related_metric, corr_value, change_a, change_b
                )
                
                if relationship:
                    relationships.append(relationship)
        
        return relationships
    
    def _classify_relationship(self, metric_a: str, metric_b: str,
                               correlation: float, change_a: float,
                               change_b: float) -> Optional[MetricRelationship]:
        """
        Classify relationship between two metrics.
        
        Returns:
            MetricRelationship or None if weak relationship
        """
        # Determine relationship type
        if abs(correlation) < 0.3:
            rel_type = "INDEPENDENT"
        elif correlation > 0.5:
            rel_type = "POSITIVE"
        elif correlation < -0.5:
            rel_type = "NEGATIVE"
        else:
            rel_type = "WEAK"
        
        # Generate business insight
        insight = self._generate_insight(
            metric_a, metric_b, correlation, change_a, change_b
        )
        
        if not insight:
            return None
        
        return MetricRelationship(
            metric_a=metric_a,
            metric_b=metric_b,
            correlation=correlation,
            change_a=change_a,
            change_b=change_b,
            relationship_type=rel_type,
            business_insight=insight
        )
    
    def _generate_insight(self, metric_a: str, metric_b: str,
                         correlation: float, change_a: float,
                         change_b: float) -> Optional[str]:
        """
        Generate business insight from metric relationship.
        
        Returns:
            Insight string or None
        """
        # Significant changes with good correlation warrant insights
        if abs(change_a) < 10 and abs(change_b) < 10:
            return None
        
        if correlation > 0.5:  # Positive correlation
            if change_a > 0 and change_b > 0:
                return f"{metric_a} and {metric_b} both increased together (corr: {correlation:.2f})"
            elif change_a < 0 and change_b < 0:
                return f"{metric_a} and {metric_b} both decreased together (corr: {correlation:.2f})"
            elif (change_a > 0 and change_b < 0) or (change_a < 0 and change_b > 0):
                return f"{metric_a} and {metric_b} moved in opposite directions despite positive correlation"
        
        elif correlation < -0.5:  # Negative correlation
            if (change_a > 0 and change_b > 0) or (change_a < 0 and change_b < 0):
                return f"{metric_a} and {metric_b} moved in same direction despite negative correlation"
            elif (change_a > 0 and change_b < 0) or (change_a < 0 and change_b > 0):
                return f"{metric_a} and {metric_b} moved inversely as expected (corr: {correlation:.2f})"
        
        return None
