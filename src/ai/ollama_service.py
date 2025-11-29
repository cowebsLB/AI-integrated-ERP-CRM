"""
Ollama service wrapper for TinyLlama AI functionality.
"""
import logging
from typing import Optional, List

logger = logging.getLogger(__name__)

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    logger.warning("Ollama library not available. Install with: pip install ollama")

import config


class OllamaService:
    """Service for interacting with TinyLlama via Ollama."""
    
    def __init__(self, model_name: str = "tinyllama"):
        self.model_name = model_name
        self.available = OLLAMA_AVAILABLE
        
        if self.available:
            try:
                # Test connection - just check if we can call ollama
                # Don't fail if list() has issues, we'll handle that in ensure_model
                try:
                    ollama.list()
                except:
                    pass  # List might fail but service might still work
                logger.info(f"Ollama service initialized (model: {model_name})")
            except Exception as e:
                logger.error(f"Failed to connect to Ollama: {e}")
                logger.info("Make sure Ollama is running. Install from: https://ollama.ai")
                self.available = False
        else:
            logger.warning("Ollama not available. Install with: pip install ollama")
    
    def is_available(self) -> bool:
        """Check if Ollama service is available."""
        return self.available and OLLAMA_AVAILABLE
    
    def ensure_model(self) -> bool:
        """Ensure the model is downloaded."""
        if not self.is_available():
            return False
        
        try:
            models = ollama.list()
            # Handle different response formats
            if isinstance(models, dict):
                model_list = models.get('models', [])
            elif isinstance(models, list):
                model_list = models
            else:
                model_list = []
            
            # Extract model names
            model_names = []
            for m in model_list:
                if isinstance(m, dict):
                    model_names.append(m.get('name', ''))
                elif isinstance(m, str):
                    model_names.append(m)
            
            if self.model_name not in model_names:
                logger.info(f"Downloading {self.model_name} model (this may take a while)...")
                ollama.pull(self.model_name)
                logger.info(f"Model {self.model_name} downloaded successfully")
            
            return True
        except KeyError as e:
            logger.error(f"Error accessing model list: {e}")
            # Try to pull anyway - might work if model exists but list format is different
            try:
                ollama.pull(self.model_name)
                return True
            except:
                return False
        except Exception as e:
            logger.error(f"Error ensuring model: {e}")
            return False
    
    def generate_response(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        system: Optional[str] = None
    ) -> str:
        """
        Generate a response from TinyLlama via Ollama.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            system: System message
            
        Returns:
            Generated response text
        """
        if not self.is_available():
            return "Ollama service is not available. Please install Ollama and ensure it's running."
        
        if not self.ensure_model():
            return "Failed to load model. Please check Ollama installation."
        
        try:
            options = {}
            if max_tokens:
                options['num_predict'] = max_tokens
            if temperature is not None:
                options['temperature'] = temperature
            
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            
            response = ollama.chat(
                model=self.model_name,
                messages=messages,
                options=options
            )
            
            return response['message']['content']
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"Error generating response: {str(e)}"
    
    def chat(self, message: str, conversation_history: Optional[List[dict]] = None) -> str:
        """
        Chat interface with conversation history support.
        
        Args:
            message: User message
            conversation_history: List of previous messages in format [{"role": "user/assistant", "content": "..."}]
            
        Returns:
            Assistant response
        """
        if not self.is_available():
            return "Ollama service is not available."
        
        if not self.ensure_model():
            return "Failed to load model."
        
        try:
            messages = []
            
            # Add system message
            messages.append({
                "role": "system",
                "content": "You are a helpful AI assistant for an ERP-CRM system."
            })
            
            # Add conversation history
            if conversation_history:
                for msg in conversation_history:
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    if role in ["user", "assistant"]:
                        messages.append({"role": role, "content": content})
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            response = ollama.chat(
                model=self.model_name,
                messages=messages
            )
            
            return response['message']['content']
            
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            return f"Error: {str(e)}"

