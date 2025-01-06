"""
Base LLM service interface.
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class LLMService(ABC):
    """Base class for LLM services"""
    
    @abstractmethod
    def __init__(self, model_name: str, **kwargs):
        """Initialize LLM service
        
        Args:
            model_name: Name of the model to use
            **kwargs: Additional model-specific parameters
        """
        self.model_name = model_name
        self.kwargs = kwargs
    
    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate text based on the prompt
        
        Args:
            prompt: Input prompt text
            
        Returns:
            Generated text response
        """
        pass
    
    @abstractmethod
    def extract_operation(self, text: str) -> str:
        """Extract operation from text
        
        Args:
            text: Input text to analyze
            
        Returns:
            Extracted operation
        """
        pass
    
    @abstractmethod
    def extract_filename(self, text: str, available_files: list) -> str:
        """Extract filename from text
        
        Args:
            text: Input text to analyze
            available_files: List of available files to match against
            
        Returns:
            Extracted filename
        """
        pass

