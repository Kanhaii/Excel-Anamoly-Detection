"""
AI prompt templates for Ollama.
"""

from config.settings import AI_PROMPT_TEMPLATE

class PromptTemplates:
    """Collection of prompt templates for AI analysis."""
    
    @staticmethod
    def get_analysis_prompt(analysis_data: str) -> str:
        """
        Get main analysis prompt.
        
        Args:
            analysis_data: Structured analytical results as JSON string
        
        Returns:
            Formatted prompt for Ollama
        """
        return AI_PROMPT_TEMPLATE.format(analysis_data=analysis_data)
    
    @staticmethod
    def get_summary_prompt(anomalies: str, relationships: str) -> str:
        """
        Get executive summary prompt.
        
        Args:
            anomalies: Description of detected anomalies
            relationships: Description of metric relationships
        
        Returns:
            Formatted prompt
        """
        return f"""You are a business analyst. Based on the following data analysis, 
write a concise executive summary (2-3 sentences) suitable for a business stakeholder.

Anomalies Detected:
{anomalies}

Metric Relationships:
{relationships}

Provide actionable insights without technical jargon."""
    
    @staticmethod
    def get_alert_prompt(metric: str, change: float, severity: str,
                         current: float, baseline: float) -> str:
        """
        Get email alert generation prompt.
        
        Args:
            metric: Metric name
            change: Percentage change
            severity: Severity level
            current: Current value
            baseline: Baseline value
        
        Returns:
            Formatted prompt
        """
        return f"""Generate a brief business-friendly alert message for this anomaly:

Metric: {metric}
Current Value: {current:,.2f}
Baseline: {baseline:,.2f}
Change: {change:+.1f}%
Severity: {severity}

The alert should:
1. Clearly state what changed
2. Explain the potential business impact
3. Suggest one or two investigation areas
4. Keep it to 3-4 sentences

Alert message:"""
    
    @staticmethod
    def get_investigation_prompt(metric: str, change: float, related_metrics: str) -> str:
        """
        Get investigation recommendation prompt.
        
        Args:
            metric: Primary metric with anomaly
            change: Percentage change
            related_metrics: Description of related metric changes
        
        Returns:
            Formatted prompt
        """
        return f"""Based on this business data anomaly, what should we investigate?

Primary Anomaly:
Metric: {metric}
Change: {change:+.1f}%

Related Metrics:
{related_metrics}

Provide 3-5 specific investigation questions a business analyst should ask."""
