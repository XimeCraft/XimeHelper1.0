import os
from .ollama_client import OllamaClient
from flask import current_app

class ChatService:
    def __init__(self):
        self.client = OllamaClient()
    
    async def get_response(self, prompt):
        """
        Get response from Ollama LLM

        Args:
            prompt (str): Complete prompt text
            
        Returns:
            str: LLM response text
        """
        try:
            response = await self.client.create_chat_completion(prompt)
            return response
        
        except Exception as e:
            current_app.logger.error(f"Error in ChatService: {str(e)}")
            return "Sorry, I encountered an error. Please try again."
            
    async def __del__(self):
        """Cleanup when service is destroyed"""
        if hasattr(self, 'client'):
            await self.client.close()