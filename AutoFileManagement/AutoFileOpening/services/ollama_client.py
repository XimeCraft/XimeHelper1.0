import httpx
import json
from flask import current_app

class OllamaClient:
    def __init__(self):
        # Required configurations - will raise KeyError if not found
        self.model = current_app.config['AUTO_FILE_OLLAMA_MODEL']
        self.temperature = current_app.config['AUTO_FILE_OLLAMA_TEMPERATURE']
        self.base_url = current_app.config['AUTO_FILE_OLLAMA_URL']
        self.max_tokens = current_app.config['AUTO_FILE_OLLAMA_MAX_PROMPT_TOKENS']
        
        # Set timeout to 60 seconds
        timeout = httpx.Timeout(60.0, connect=30.0)
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout
        )
    
    async def create_chat_completion(self, prompt, model=None):
        """
        Call Ollama API to get response
        
        Args:
            prompt (str): Complete prompt text
            model (str, optional): Model name to use
            
        Returns:
            str: API response text
        """
        try:
            # Real API call
            current_app.logger.info(f'Calling Ollama API with model {model or self.model}')
            response = await self.client.post(
                '/api/generate',
                json={
                    'model': model or self.model,
                    'prompt': prompt,
                    'stream': False,
                    'temperature': self.temperature
                }
            )
            response.raise_for_status()
            
            # Parse response line by line
            response_text = ""
            for line in response.text.strip().split('\n'):
                try:
                    data = json.loads(line)
                    if 'response' in data:
                        response_text += data['response']
                except json.JSONDecodeError:
                    continue
            
            current_app.logger.info('Successfully received response from Ollama API')
            return response_text.strip()
            
        except httpx.TimeoutException:
            current_app.logger.error("Ollama service timeout")
            raise Exception("Ollama service timeout. Please check if the service is running correctly.")
        except httpx.HTTPError as e:
            current_app.logger.error(f"Ollama API error: {str(e)}")
            raise Exception(f"Ollama API error: {str(e)}")
        except Exception as e:
            current_app.logger.error(f"Unexpected error when calling Ollama: {str(e)}", exc_info=True)
            raise
            
    async def close(self):
        """Close the HTTP client"""
        if hasattr(self, 'client'):
            await self.client.aclose() 