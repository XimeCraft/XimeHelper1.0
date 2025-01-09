import os
from flask import current_app
from .openai_client import OpenAIClient
from .ollama_client import OllamaClient

class ChatService:
    def __init__(self):
        if current_app.config['AUTO_FILE_OLLAMA_ENABLED']:
            self.client = OllamaClient()
        elif current_app.config['AUTO_FILE_OPENAI_ENABLED']:
            self.client = OpenAIClient()
        else:
            raise ValueError("No LLM service is enabled. Please enable either Ollama or OpenAI in config.")
        print("==========chat_service==========")
        print(self.client)
        print("==========chat_service==========")

    def get_response(self, prompt):
        """
        Get response from LLM service (either Ollama or OpenAI)
        
        Args:
            prompt (str): Complete prompt text
            
        Returns:
            str: LLM response text
        """
        try:
            response = self.client.create_chat_completion(prompt)
            return response
        
        except Exception as e:
            print(f"Error in ChatService: {str(e)}")
            return "Sorry, I encountered an error. Please try again."