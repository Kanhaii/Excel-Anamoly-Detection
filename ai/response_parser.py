"""
Response parsing utilities for LLM output.
"""

import json
from typing import Dict, Any, Optional, List
from utils.logging_config import get_logger

logger = get_logger("response_parser")

class ResponseParser:
    """Parse and validate LLM responses."""
    
    @staticmethod
    def extract_json(text: str) -> Optional[Dict[str, Any]]:
        """
        Extract JSON from text, handling markdown code blocks.
        
        Args:
            text: Text containing JSON
        
        Returns:
            Parsed JSON dict or None
        """
        if not text:
            return None
        
        # Try direct parsing first
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # Look for code blocks
        if "```json" in text:
            json_start = text.find("```json") + 7
            json_end = text.find("```", json_start)
            if json_end > json_start:
                try:
                    return json.loads(text[json_start:json_end].strip())
                except json.JSONDecodeError:
                    pass
        
        if "```" in text:
            json_start = text.find("```") + 3
            json_end = text.find("```", json_start)
            if json_end > json_start:
                try:
                    return json.loads(text[json_start:json_end].strip())
                except json.JSONDecodeError:
                    pass
        
        # Look for {" pattern
        json_start = text.find('{"')
        if json_start >= 0:
            json_end = text.rfind('}')
            if json_end > json_start:
                try:
                    return json.loads(text[json_start:json_end+1])
                except json.JSONDecodeError:
                    pass
        
        logger.warning("Could not extract valid JSON from response")
        return None
    
    @staticmethod
    def validate_insight_response(data: Dict[str, Any]) -> bool:
        """
        Validate that response has required insight fields.
        
        Args:
            data: Response dict
        
        Returns:
            True if valid
        """
        required_fields = ['executive_summary', 'key_changes', 
                          'business_implications', 'recommended_actions']
        
        for field in required_fields:
            if field not in data:
                logger.warning(f"Missing required field: {field}")
                return False
        
        # Check types
        if not isinstance(data['executive_summary'], str):
            return False
        if not isinstance(data['key_changes'], list):
            return False
        if not isinstance(data['business_implications'], list):
            return False
        if not isinstance(data['recommended_actions'], list):
            return False
        
        return True
    
    @staticmethod
    def sanitize_text(text: str, max_length: int = None) -> str:
        """
        Sanitize text output from LLM.
        
        Args:
            text: Text to sanitize
            max_length: Maximum length (truncate if needed)
        
        Returns:
            Sanitized text
        """
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Truncate if needed
        if max_length and len(text) > max_length:
            text = text[:max_length-3] + "..."
        
        return text
