import os
import openai
from flask import current_app

class OpenAIClient:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        
        if not self.api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        openai.api_key = self.api_key
    
    def create_chat_completion(self, prompt, model="gpt-3.5-turbo"):
        """
        Call OpenAI API to get response
        
        Args:
            prompt (str): Complete prompt text
            model (str): Model name to use
            
        Returns:
            str: API response text
        """

        print(self.system_prompt)
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7  # Add some creativity but not too much
            )
            return response.choices[0].message.content
        
        except Exception as e:
            current_app.logger.error(f"OpenAI API error: {str(e)}")
            raise