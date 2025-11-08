"""
Ollama LLM Client.

This is the ONLY module that directly imports the ollama library.
It provides a centralized interface for LLM interactions used by tools.
"""

import logging
from typing import List, Dict, Optional

try:
    import ollama
except ImportError:
    ollama = None
    logging.warning("ollama package not installed. Install with: pip install ollama")

logger = logging.getLogger(__name__)


class OllamaClient:
    """
    Centralized client for Ollama LLM interactions.
    
    This client is used by tools (not AutoGen agents directly) for
    specific LLM tasks like summarization and content analysis.
    """
    
    def __init__(
        self,
        model_name: str = "llama3",
        base_url: str = "http://localhost:11434",
    ):
        """
        Initialize the Ollama client.
        
        Args:
            model_name: Name of the Ollama model to use
            base_url: Base URL for the Ollama server
        """
        self.model_name = model_name
        self.base_url = base_url
        
        if ollama is None:
            raise ImportError(
                "ollama package is not installed. "
                "Install it with: pip install ollama"
            )
    
    def generate(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: float = 0.7,
    ) -> str:
        """
        Generate text using Ollama.
        
        Args:
            prompt: The prompt to send to the model
            system_message: Optional system message for context
            temperature: Sampling temperature (0.0 to 1.0)
            
        Returns:
            Generated text response
        """
        try:
            messages = []
            
            if system_message:
                messages.append({
                    "role": "system",
                    "content": system_message,
                })
            
            messages.append({
                "role": "user",
                "content": prompt,
            })
            
            response = ollama.chat(
                model=self.model_name,
                messages=messages,
                options={
                    "temperature": temperature,
                }
            )
            
            return response['message']['content']
        
        except Exception as e:
            logger.error(f"Error generating text with Ollama: {e}")
            return f"Error: {str(e)}"
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
    ) -> str:
        """
        Multi-turn chat with Ollama.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0.0 to 1.0)
            
        Returns:
            Generated response
        """
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=messages,
                options={
                    "temperature": temperature,
                }
            )
            
            return response['message']['content']
        
        except Exception as e:
            logger.error(f"Error in chat with Ollama: {e}")
            return f"Error: {str(e)}"
    
    def summarize(
        self,
        text: str,
        max_length: int = 200,
    ) -> str:
        """
        Summarize text using Ollama.
        
        Args:
            text: The text to summarize
            max_length: Maximum length of summary in words
            
        Returns:
            Summarized text
        """
        system_message = (
            f"You are a content summarization expert. "
            f"Summarize the following text in {max_length} words or less. "
            f"Focus on key points and maintain clarity."
        )
        
        return self.generate(
            prompt=text,
            system_message=system_message,
            temperature=0.5,
        )
    
    def assess_quality(
        self,
        title: str,
        description: str,
    ) -> Dict[str, any]:
        """
        Assess content quality using Ollama.
        
        Args:
            title: Content title
            description: Content description
            
        Returns:
            Dict with quality score and reasoning
        """
        system_message = (
            "You are a content quality analyst. "
            "Rate the quality and relevance of content on a scale of 1-10. "
            "Respond with ONLY a JSON object containing 'score' (integer) "
            "and 'reasoning' (string)."
        )
        
        prompt = f"Title: {title}\n\nDescription: {description}"
        
        try:
            response = self.generate(
                prompt=prompt,
                system_message=system_message,
                temperature=0.3,
            )
            
            # Try to parse JSON response
            import json
            result = json.loads(response)
            return result
        
        except Exception as e:
            logger.error(f"Error assessing quality: {e}")
            return {
                "score": 5,
                "reasoning": "Unable to assess quality due to error",
            }




