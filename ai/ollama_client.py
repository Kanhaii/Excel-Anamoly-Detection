"""
Ollama client for LLM integration.
"""

import requests
import json
from typing import Optional, Dict, Any
from utils.logging_config import get_logger
from config.settings import OLLAMA_BASE_URL, OLLAMA_MODEL, OLLAMA_TIMEOUT

logger = get_logger("ollama_client")

class OllamaClient:
    """Client for Ollama local LLM service."""
    
    def __init__(self, base_url: str = OLLAMA_BASE_URL, model: str = OLLAMA_MODEL):
        """
        Initialize Ollama client.
        
        Args:
            base_url: Ollama service base URL
            model: Model name to use
        """
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.timeout = OLLAMA_TIMEOUT
    
    def is_available(self) -> bool:
        """
        Check if Ollama service is running.
        
        Returns:
            True if service is available
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Ollama service not available: {str(e)}")
            return False
    
    def is_model_available(self) -> bool:
        """
        Check if the configured model is available.
        
        Returns:
            True if model is available
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            if response.status_code != 200:
                return False
            
            data = response.json()
            models = data.get('models', [])
            model_names = [m.get('name', '').split(':')[0] for m in models]
            
            return self.model in model_names
        except Exception as e:
            logger.warning(f"Error checking model availability: {str(e)}")
            return False
    
    def get_available_models(self) -> list:
        """
        Get list of available models.
        
        Returns:
            List of model names
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            if response.status_code != 200:
                return []
            
            data = response.json()
            models = data.get('models', [])
            return [m.get('name', '') for m in models]
        except Exception as e:
            logger.warning(f"Error fetching models: {str(e)}")
            return []
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> Optional[str]:
        """
        Generate text using Ollama.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
        
        Returns:
            Generated text or None if error
        """
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
            
            if system_prompt:
                payload["system"] = system_prompt
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                logger.error(f"Ollama error: {response.status_code} - {response.text}")
                return None
            
            data = response.json()
            generated_text = data.get('response', '').strip()
            
            logger.info(f"Generated text ({len(generated_text)} chars) from Ollama")
            return generated_text
        
        except requests.exceptions.Timeout:
            logger.error(f"Ollama request timeout after {self.timeout}s")
            return None
        except Exception as e:
            logger.error(f"Error calling Ollama: {str(e)}")
            return None
    
    def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Generate JSON response from Ollama.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
        
        Returns:
            Parsed JSON dict or None if error
        """
        text = self.generate(prompt, system_prompt)
        
        if not text:
            return None
        
        try:
            # Try to extract JSON from response
            # Handle cases where LLM adds markdown code blocks
            if "```json" in text:
                json_start = text.find("```json") + 7
                json_end = text.find("```", json_start)
                text = text[json_start:json_end].strip()
            elif "```" in text:
                json_start = text.find("```") + 3
                json_end = text.find("```", json_start)
                text = text[json_start:json_end].strip()
            
            data = json.loads(text)
            logger.info("Successfully parsed JSON response from Ollama")
            return data
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Ollama response as JSON: {str(e)}")
            logger.debug(f"Response text: {text[:500]}")
            return None
