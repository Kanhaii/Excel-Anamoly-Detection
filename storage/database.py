"""
Database storage and persistence.
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from utils.logging_config import get_logger
from config.settings import DB_PATH

logger = get_logger("database")

class AlertDatabase:
    """SQLite database for alert storage."""
    
    def __init__(self, db_path: Path = DB_PATH):
        """
        Initialize database.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self) -> None:
        """
        Initialize database schema.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS alerts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        metric TEXT NOT NULL,
                        severity TEXT NOT NULL,
                        current_value REAL,
                        baseline_value REAL,
                        change_percent REAL,
                        change_absolute REAL,
                        z_score REAL,
                        email_sent BOOLEAN DEFAULT 0,
                        email_recipient TEXT,
                        ai_summary TEXT,
                        notes TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS analysis_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        analysis_data TEXT NOT NULL,
                        anomaly_count INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.commit()
                logger.info("Database initialized")
        
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
    
    def save_alert(self, alert_dict: Dict) -> bool:
        """
        Save alert to database.
        
        Args:
            alert_dict: Alert data as dictionary
        
        Returns:
            True if saved successfully
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO alerts
                    (timestamp, metric, severity, current_value, baseline_value,
                     change_percent, change_absolute, z_score, email_sent,
                     email_recipient, ai_summary, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    alert_dict.get('timestamp'),
                    alert_dict.get('metric'),
                    alert_dict.get('severity'),
                    alert_dict.get('current_value'),
                    alert_dict.get('baseline_value'),
                    alert_dict.get('change_percent'),
                    alert_dict.get('change_absolute'),
                    alert_dict.get('z_score'),
                    alert_dict.get('email_sent', False),
                    alert_dict.get('email_recipient'),
                    alert_dict.get('ai_summary'),
                    alert_dict.get('notes')
                ))
                conn.commit()
                logger.info(f"Alert saved: {alert_dict.get('metric')}")
                return True
        
        except Exception as e:
            logger.error(f"Error saving alert: {str(e)}")
            return False
    
    def get_recent_alerts(self, limit: int = 20) -> List[Dict]:
        """
        Get recent alerts.
        
        Args:
            limit: Maximum number of alerts
        
        Returns:
            List of alert dictionaries
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM alerts
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (limit,))
                return [dict(row) for row in cursor.fetchall()]
        
        except Exception as e:
            logger.error(f"Error fetching alerts: {str(e)}")
            return []
    
    def get_critical_alerts(self) -> List[Dict]:
        """
        Get critical severity alerts.
        
        Returns:
            List of critical alerts
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM alerts
                    WHERE severity = 'CRITICAL'
                    ORDER BY timestamp DESC
                """)
                return [dict(row) for row in cursor.fetchall()]
        
        except Exception as e:
            logger.error(f"Error fetching critical alerts: {str(e)}")
            return []
