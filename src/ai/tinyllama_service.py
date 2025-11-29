"""
TinyLlama service wrapper for AI functionality.
"""
import os
from pathlib import Path
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

try:
    from transformers import AutoTokenizer, AutoModelForCausalLM
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("Transformers library not available. AI features will be disabled.")

import config

class TinyLlamaService:
    """Service for interacting with TinyLlama model."""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu" if TRANSFORMERS_AVAILABLE else None
        self._load_model()
        
    def _load_model(self):
        """Load the TinyLlama model and tokenizer."""
        if not TRANSFORMERS_AVAILABLE:
            logger.error("Transformers library not available. Cannot load TinyLlama.")
            return
            
        try:
            model_path = config.TINYLLAMA_PATH if config.TINYLLAMA_PATH else config.TINYLLAMA_MODEL_NAME
            
            logger.info(f"Loading TinyLlama model from: {model_path}")
            logger.info(f"Using device: {self.device}")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_path,
                trust_remote_code=True
            )
            
            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                model_path,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None,
                trust_remote_code=True
            )
            
            if self.device == "cpu":
                self.model = self.model.to(self.device)
                
            self.model.eval()
            logger.info("TinyLlama model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading TinyLlama model: {e}")
            self.model = None
            self.tokenizer = None
    
    def is_available(self) -> bool:
        """Check if the AI service is available."""
        return self.model is not None and self.tokenizer is not None
    
    def generate_response(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None
    ) -> str:
        """
        Generate a response from TinyLlama.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            
        Returns:
            Generated response text
        """
        if not self.is_available():
            return "AI service is not available. Please check your TinyLlama installation."
        
        try:
            max_tokens = max_tokens or config.AI_MAX_TOKENS
            temperature = temperature or config.AI_TEMPERATURE
            top_p = top_p or config.AI_TOP_P
            
            # Tokenize input
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            
            # Generate
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Remove the prompt from the response
            if response.startswith(prompt):
                response = response[len(prompt):].strip()
            
            return response
            
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
            return "AI service is not available."
        
        # Build prompt with conversation history
        prompt = ""
        if conversation_history:
            for msg in conversation_history:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                prompt += f"{role.capitalize()}: {content}\n"
        
        prompt += f"User: {message}\nAssistant:"
        
        return self.generate_response(prompt)

