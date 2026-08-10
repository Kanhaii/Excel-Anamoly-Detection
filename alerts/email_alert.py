"""
Email alert system.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List
from utils.logging_config import get_logger
from config.settings import (
    SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD,
    ALERT_EMAIL, SMTP_USE_TLS
)

logger = get_logger("email_alert")

class EmailAlert:
    """Send email alerts for anomalies."""
    
    def __init__(self, smtp_server: str = SMTP_SERVER,
                 smtp_port: int = SMTP_PORT,
                 username: str = SMTP_USERNAME,
                 password: str = SMTP_PASSWORD,
                 from_email: str = SMTP_USERNAME):
        """
        Initialize email alert system.
        
        Args:
            smtp_server: SMTP server address
            smtp_port: SMTP port
            username: SMTP username
            password: SMTP password
            from_email: From email address
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email
    
    def send_alert(self, to_email: str, subject: str, body: str,
                   html_body: Optional[str] = None) -> bool:
        """
        Send email alert.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Plain text body
            html_body: Optional HTML body
        
        Returns:
            True if sent successfully
        """
        # Validate inputs
        if not self._validate_config():
            logger.error("Email configuration incomplete")
            return False
        
        if not to_email or '@' not in to_email:
            logger.error(f"Invalid recipient email: {to_email}")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            # Attach plain text
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach HTML if provided
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))
            
            # Send
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10) as server:
                if SMTP_USE_TLS:
                    server.starttls()
                
                server.login(self.username, self.password)
                server.send_message(msg)
            
            logger.info(f"Email alert sent to {to_email}")
            return True
        
        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP authentication failed")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False
    
    def send_critical_alert(self, metric: str, change: float,
                           current: float, baseline: float,
                           to_email: Optional[str] = ALERT_EMAIL) -> bool:
        """
        Send critical anomaly alert.
        
        Args:
            metric: Metric name
            change: Percentage change
            current: Current value
            baseline: Baseline value
            to_email: Recipient email
        
        Returns:
            True if sent
        """
        subject = f"🚨 Business Alert: Critical Anomaly in {metric}"
        
        body = f"""Business Data Alert

Metric: {metric}
Change: {change:+.1f}%
Current Value: {current:,.2f}
Baseline: {baseline:,.2f}

This metric has significantly deviated from normal behavior.
Please investigate."""
        
        html_body = f"""<html><body>
<h2>🚨 Business Alert: Critical Anomaly Detected</h2>
<p><strong>Metric:</strong> {metric}</p>
<p><strong>Change:</strong> <span style="color: red; font-weight: bold;">{change:+.1f}%</span></p>
<p><strong>Current Value:</strong> {current:,.2f}</p>
<p><strong>Baseline:</strong> {baseline:,.2f}</p>
<p>This metric has significantly deviated from normal behavior. Please investigate.</p>
</body></html>"""
        
        return self.send_alert(to_email, subject, body, html_body)
    
    def _validate_config(self) -> bool:
        """
        Validate email configuration.
        
        Returns:
            True if valid
        """
        return all([
            self.smtp_server,
            self.smtp_port > 0,
            self.username,
            self.password,
            self.from_email
        ])
