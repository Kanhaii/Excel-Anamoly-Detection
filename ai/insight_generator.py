"""
AI insight generation and LLM integration.
"""

import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from ai.ollama_client import OllamaClient
from ai.prompts import PromptTemplates
from utils.helpers import convert_to_native_python
from utils.logging_config import get_logger

logger = get_logger("insight_generator")

@dataclass
class AIInsight:
    """AI-generated insight."""
    executive_summary: str
    key_changes: List[str]
    business_implications: List[str]
    recommended_actions: List[str]
    raw_response: str
    generation_error: Optional[str] = None

class InsightGenerator:
    """Generate AI insights using Ollama."""
    
    def __init__(self, ollama_client: Optional[OllamaClient] = None):
        """
        Initialize insight generator.
        
        Args:
            ollama_client: OllamaClient instance (create default if None)
        """
        self.client = ollama_client or OllamaClient()
    
    def generate_analysis_insight(self, analysis_data: Dict[str, Any]) -> AIInsight:
        """
        Generate AI insight from analytical results.
        
        Args:
            analysis_data: Structured analysis results as dict
        
        Returns:
            AIInsight object
        """
        # Convert to JSON string
        try:
            analysis_json = json.dumps(
                convert_to_native_python(analysis_data),
                indent=2
            )
        except Exception as e:
            logger.error(f"Error converting analysis data to JSON: {str(e)}")
            return self._error_insight(f"Data conversion failed: {str(e)}")
        
        # Get prompt
        prompt = PromptTemplates.get_analysis_prompt(analysis_json)
        
        # Check if Ollama is available
        if not self.client.is_available():
            error_msg = "Ollama service not available at " + self.client.base_url
            logger.error(error_msg)
            return self._error_insight(error_msg)
        
        if not self.client.is_model_available():
            error_msg = f"Model '{self.client.model}' not available in Ollama"
            logger.error(error_msg)
            return self._error_insight(error_msg)
        
        # Generate response
        logger.info(f"Generating AI insight using {self.client.model}...")
        response = self.client.generate_json(prompt)
        
        if response is None:
            # Try to parse as plain text fallback
            text_response = self.client.generate(prompt)
            if text_response:
                return self._parse_text_response(text_response)
            return self._error_insight("Failed to generate insight from Ollama")
        
        return self._parse_response(response)
    
    def _parse_response(self, response: Dict[str, Any]) -> AIInsight:
        """
        Parse JSON response from Ollama.
        
        Args:
            response: JSON response dict
        
        Returns:
            AIInsight object
        """
        try:
            return AIInsight(
                executive_summary=response.get('executive_summary', 'No summary generated'),
                key_changes=response.get('key_changes', []),
                business_implications=response.get('business_implications', []),
                recommended_actions=response.get('recommended_actions', []),
                raw_response=json.dumps(response),
                generation_error=None
            )
        except Exception as e:
            logger.error(f"Error parsing Ollama response: {str(e)}")
            return self._error_insight(f"Response parsing failed: {str(e)}")
    
    def _parse_text_response(self, text: str) -> AIInsight:
        """
        Parse plain text response as fallback.
        
        Args:
            text: Plain text response
        
        Returns:
            AIInsight object
        """
        lines = text.strip().split('\n')
        return AIInsight(
            executive_summary=text[:300] if text else "Unable to generate summary",
            key_changes=lines[:3] if len(lines) > 0 else [],
            business_implications=[],
            recommended_actions=[],
            raw_response=text,
            generation_error="Parsed as text due to JSON parsing failure"
        )
    
    def _error_insight(self, error: str) -> AIInsight:
        """
        Create error insight.
        
        Args:
            error: Error message
        
        Returns:
            AIInsight with error flag
        """
        return AIInsight(
            executive_summary="Unable to generate AI insight.",
            key_changes=[],
            business_implications=[],
            recommended_actions=[],
            raw_response="",
            generation_error=error
        )
    
    def generate_alert_summary(self, metric: str, change: float, severity: str,
                              current: float, baseline: float) -> str:
        """
        Generate alert email summary.
        
        Args:
            metric: Metric name
            change: Percentage change
            severity: Severity level
            current: Current value
            baseline: Baseline value
        
        Returns:
            Alert message string
        """
        if not self.client.is_available():
            return f"{metric} changed by {change:+.1f}% (from {baseline:,.0f} to {current:,.0f}). Severity: {severity}"
        
        prompt = PromptTemplates.get_alert_prompt(metric, change, severity, current, baseline)
        response = self.client.generate(prompt)
        
        return response or f"{metric} changed by {change:+.1f}%"
