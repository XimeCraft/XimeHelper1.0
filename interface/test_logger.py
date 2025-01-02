"""
Test logger for debugging and testing purposes
"""
from flask import current_app
import time

class TestLogger:
    """Logger for testing and debugging purposes"""
    
    def __init__(self):
        self.start_time = None
    
    def start_execution(self, message):
        """Log the start of test execution"""
        self.start_time = time.time()
        current_app.logger.debug(f"Test execution started: {message}")
    
    def end_execution(self):
        """Log the end of test execution"""
        if self.start_time:
            duration = time.time() - self.start_time
            current_app.logger.debug(f"Test execution ended. Duration: {duration:.2f}s")
    
    def log_directory_info(self, info):
        """Log directory information"""
        current_app.logger.debug(f"Directory info: {info}")
    
    def log_prompt(self, prompt, info):
        """Log prompt information"""
        current_app.logger.debug(f"Prompt info: {info}")
        current_app.logger.debug(f"Prompt content: {prompt[:200]}...")
    
    def log_llm_response(self, response):
        """Log LLM response"""
        current_app.logger.debug(f"LLM response: {response}")
    
    def log_file_info(self, info):
        """Log file information"""
        current_app.logger.debug(f"File info: {info}") 