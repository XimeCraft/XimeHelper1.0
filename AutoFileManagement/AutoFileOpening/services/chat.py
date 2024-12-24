import os
from .openai_client import OpenAIClient

class ChatService:
    def __init__(self):
        self.client = OpenAIClient()
    
    def get_response(self, prompt):
        """
        Get response from ChatGPT
        
        Args:
            prompt (str): Complete prompt text
            
        Returns:
            str: ChatGPT response text
        """

        try:
            response = self.client.create_chat_completion(prompt)
            return response
        
        except Exception as e:
            print(f"Error in ChatService: {str(e)}")
            return "Sorry, I encountered an error. Please try again."