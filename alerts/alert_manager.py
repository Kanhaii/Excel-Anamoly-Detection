"""
Alert management and history.
"""

import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from utils.logging_config import get_logger
from config.settings import ALERT_HISTORY_CSV

logger = get_logger("alert_manager")

@dataclass
class Alert:
    """Alert record."""
    timestamp: str
    metric: str
    severity: str
    current_value: float
    baseline_value: float
    change_percent: float
    change_absolute: Optional[float]
    z_score: Optional[float]
    email_sent: bool = False
    email_recipient: Optional[str] = None
    ai_summary: Optional[str] = None
    notes: Optional[str] = field(default="")

class AlertManager:
    """Manage alert history and persistence."""
    
    def __init__(self, history_file: Path = ALERT_HISTORY_CSV):
        """
        Initialize alert manager.
        
        Args:
            history_file: Path to alert history CSV
        """
        self.history_file = history_file
        self.alerts: List[Alert] = []
        self._load_history()
    
    def add_alert(self, alert: Alert) -> None:
        """
        Add an alert to history.
        
        Args:
            alert: Alert object
        """
        self.alerts.append(alert)
        self._save_history()
        logger.info(f"Alert added: {alert.metric} ({alert.severity})")
    
    def _load_history(self) -> None:
        """
        Load alert history from CSV file.
        """
        if not self.history_file.exists():
            return
        
        try:
            with open(self.history_file, 'r', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    alert = Alert(
                        timestamp=row['timestamp'],
                        metric=row['metric'],
                        severity=row['severity'],
                        current_value=float(row['current_value']),
                        baseline_value=float(row['baseline_value']),
                        change_percent=float(row['change_percent']),
                        change_absolute=float(row['change_absolute']) if row['change_absolute'] else None,
                        z_score=float(row['z_score']) if row['z_score'] else None,
                        email_sent=row.get('email_sent', 'false').lower() == 'true',
                        email_recipient=row.get('email_recipient'),
                        ai_summary=row.get('ai_summary'),
                        notes=row.get('notes', '')
                    )
                    self.alerts.append(alert)
            
            logger.info(f"Loaded {len(self.alerts)} alerts from history")
        except Exception as e:
            logger.error(f"Error loading alert history: {str(e)}")
    
    def _save_history(self) -> None:
        """
        Save alert history to CSV file.
        """
        try:
            # Ensure directory exists
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.history_file, 'w', newline='') as f:
                fieldnames = [
                    'timestamp', 'metric', 'severity', 'current_value',
                    'baseline_value', 'change_percent', 'change_absolute',
                    'z_score', 'email_sent', 'email_recipient', 'ai_summary', 'notes'
                ]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for alert in self.alerts:
                    writer.writerow({
                        'timestamp': alert.timestamp,
                        'metric': alert.metric,
                        'severity': alert.severity,
                        'current_value': f"{alert.current_value:.2f}",
                        'baseline_value': f"{alert.baseline_value:.2f}",
                        'change_percent': f"{alert.change_percent:.2f}",
                        'change_absolute': f"{alert.change_absolute:.2f}" if alert.change_absolute else "",
                        'z_score': f"{alert.z_score:.2f}" if alert.z_score else "",
                        'email_sent': str(alert.email_sent),
                        'email_recipient': alert.email_recipient or "",
                        'ai_summary': alert.ai_summary or "",
                        'notes': alert.notes or ""
                    })
            
            logger.info(f"Saved {len(self.alerts)} alerts to history")
        except Exception as e:
            logger.error(f"Error saving alert history: {str(e)}")
    
    def get_critical_alerts(self) -> List[Alert]:
        """
        Get all critical severity alerts.
        
        Returns:
            List of critical alerts
        """
        return [a for a in self.alerts if a.severity == "CRITICAL"]
    
    def get_recent_alerts(self, limit: int = 10) -> List[Alert]:
        """
        Get recent alerts.
        
        Args:
            limit: Maximum number of alerts
        
        Returns:
            List of recent alerts
        """
        return sorted(self.alerts, key=lambda a: a.timestamp, reverse=True)[:limit]
    
    def get_alerts_by_metric(self, metric: str) -> List[Alert]:
        """
        Get alerts for specific metric.
        
        Args:
            metric: Metric name
        
        Returns:
            List of matching alerts
        """
        return [a for a in self.alerts if a.metric.lower() == metric.lower()]
