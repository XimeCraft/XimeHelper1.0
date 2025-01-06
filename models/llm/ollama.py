"""
Ollama LLM service implementation.
"""
import httpx
import json
from typing import Optional, Dict, Any
from .base import LLMService

class OllamaService(LLMService):
    """Ollama LLM service implementation"""
    
    def __init__(self, model_name: str = 'deepseek-llm', **kwargs):
        """Initialize Ollama service
        
        Args:
            model_name: Name of the model to use
            **kwargs: Additional model-specific parameters
        """
        super().__init__(model_name, **kwargs)
        self.base_url = kwargs.get('base_url', 'http://localhost:11434')
        
        # Setup HTTP client
        timeout = httpx.Timeout(60.0, connect=30.0)
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout
        )
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using Ollama API
        
        Args:
            prompt: Input prompt text
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text response
            
        Raises:
            Exception: If API call fails
        """
        try:
            response = await self.client.post(
                '/api/generate',
                json={
                    'model': self.model_name,
                    'prompt': prompt,
                    'stream': False,
                    **kwargs
                }
            )
            
            response.raise_for_status()
            
            # Process streaming response
            response_text = ''
            for line in response.text.strip().split('\n'):
                try:
                    data = json.loads(line)
                    if 'response' in data:
                        response_text += data['response']
                except json.JSONDecodeError:
                    continue
                    
            return response_text.strip()
            
        except httpx.TimeoutException:
            raise Exception('Ollama service timeout. Please check if the service is running correctly.')
        except httpx.HTTPError as e:
            raise Exception(f'Ollama API error: {str(e)}')
        except Exception as e:
            raise Exception(f'Unexpected error when calling Ollama: {str(e)}')
    
    async def extract_operation(self, text: str) -> str:
        """Extract operation from text
        
        Args:
            text: Input text to analyze
            
        Returns:
            Extracted operation (open/close)
        """
        prompt = f"""
        Extract the operation from the following text. The operation should be one of: open, close.
        Only return the operation word, nothing else.
        
        Text: {text}
        """
        return await self.generate(prompt)
    
    async def extract_filename(self, text: str, available_files: list) -> str:
        """Extract filename from text
        
        Args:
            text: Input text to analyze
            available_files: List of available files to match against
            
        Returns:
            Extracted filename
        """
        files_str = '\n'.join(f'- {f}' for f in available_files)
        
        prompt = f"""
        Extract the most likely filename from the following text. 
        The filename must be one from the available files list.
        Only return the filename, nothing else.
        
        Available files:
        {files_str}
        
        Text: {text}
        """
        
        return await self.generate(prompt)
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose() 