"""
Unified AI service that supports both Ollama and Hugging Face backends.
"""
import logging
from typing import Optional, List

import config

logger = logging.getLogger(__name__)


class AIService:
    """Unified AI service that automatically selects the best available backend."""
    
    def __init__(self):
        self.ollama_service = None
        self.hf_service = None
        self.active_service = None
        
        # Try Ollama first (preferred)
        if config.USE_OLLAMA:
            try:
                from src.ai.ollama_service import OllamaService
                self.ollama_service = OllamaService(model_name=config.OLLAMA_MODEL)
                if self.ollama_service.is_available():
                    self.active_service = self.ollama_service
                    logger.info("Using Ollama backend for AI")
            except Exception as e:
                logger.warning(f"Ollama not available: {e}")
        
        # Fallback to Hugging Face
        if not self.active_service:
            try:
                from src.ai.tinyllama_service import TinyLlamaService
                self.hf_service = TinyLlamaService()
                if self.hf_service.is_available():
                    self.active_service = self.hf_service
                    logger.info("Using Hugging Face backend for AI")
            except Exception as e:
                logger.warning(f"Hugging Face not available: {e}")
        
        if not self.active_service:
            logger.warning("No AI service available. Install Ollama or configure Hugging Face model.")
    
    def is_available(self) -> bool:
        """Check if AI service is available."""
        return self.active_service is not None and self.active_service.is_available()
    
    def generate_response(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> str:
        """Generate a response."""
        if not self.is_available():
            return "AI service is not available. Please install Ollama or configure the model."
        
        return self.active_service.generate_response(
            prompt=prompt,
            max_tokens=max_tokens or config.AI_MAX_TOKENS,
            temperature=temperature or config.AI_TEMPERATURE
        )
    
    def chat(self, message: str, conversation_history: Optional[List[dict]] = None) -> str:
        """Chat interface."""
        if not self.is_available():
            return "AI service is not available."
        
        return self.active_service.chat(message, conversation_history)

