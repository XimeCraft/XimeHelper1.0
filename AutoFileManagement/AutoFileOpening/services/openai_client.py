import os
from openai import OpenAI
from flask import current_app
import tiktoken
from dotenv import load_dotenv

class OpenAIClient:
    def __init__(self):
        # Force reload environment variables
        load_dotenv(override=True)
        
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key not found in environment variables")
            
        self.model = current_app.config.get('AUTO_FILE_OPENAI_MODEL', 'gpt-3.5-turbo')
        self.temperature = current_app.config.get('AUTO_FILE_OPENAI_TEMPERATURE', 0.7)
        self.max_tokens = current_app.config.get('AUTO_FILE_MAX_PROMPT_TOKENS', 2000)
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.api_key)
        current_app.logger.info(f'OpenAI client initialized with model: {self.model}')
    
    def _count_tokens(self, text):
        """Count the number of tokens in the text"""
        try:
            encoding = tiktoken.encoding_for_model(self.model)
            return len(encoding.encode(text))
        except Exception as e:
            current_app.logger.warning(f"Error counting tokens: {e}")
            # Fallback: rough estimate (1 token ≈ 4 characters)
            return len(text) // 4
    
    def create_chat_completion(self, prompt, model=None):
        """
        Call OpenAI API to get response
        
        Args:
            prompt (str): Complete prompt text
            model (str, optional): Model name to use
            
        Returns:
            str: API response text
        """
        try:
            # Check token count
            token_count = self._count_tokens(prompt)
            if token_count > self.max_tokens:
                current_app.logger.warning(
                    f"Prompt size ({token_count} tokens) exceeds maximum ({self.max_tokens}). "
                    "Consider reducing the number of files or prompt length."
                )
                return "Sorry, the prompt is too long. Please try with fewer files or a shorter message."

            # Real API call
            current_app.logger.info(f'Calling OpenAI API with model {model or self.model}')
            response = self.client.chat.completions.create(
                model=model or self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature
            )
            
            current_app.logger.info('Successfully received response from OpenAI API')
            return response.choices[0].message.content
        
        except Exception as e:
            current_app.logger.error(f"OpenAI API error: {str(e)}", exc_info=True)
            raise