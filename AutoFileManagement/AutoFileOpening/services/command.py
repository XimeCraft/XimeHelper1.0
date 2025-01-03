from .chat import ChatService
from .prompt import PromptService
from .file import FileService
from flask import current_app
import os
from datetime import datetime
from interface.test_logger import TestLogger

class CommandService:
    """Service for processing user commands"""
    
    def __init__(self):
        self.chat_service = ChatService()
        self.prompt_service = PromptService()
        self.file_service = FileService()
        self.test_logger = TestLogger()
        # Maximum number of files to include in prompt
        self.max_files_in_prompt = current_app.config.get('AUTO_FILE_OPENING_MAX_FILES_IN_PROMPT', 5)

    def _format_file_info(self, file_path):
        """Format file information for display"""
        try:
            stats = os.stat(file_path)
            size = stats.st_size
            modified = datetime.fromtimestamp(stats.st_mtime)
            
            # Convert size to human readable format
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024:
                    break
                size /= 1024
            size_str = f"{size:.1f} {unit}"
            
            return {
                'name': os.path.basename(file_path),
                'path': file_path,
                'size': size_str,
                'modified': modified.strftime('%Y-%m-%d %H:%M:%S'),
                'type': os.path.splitext(file_path)[1][1:] or 'unknown'
            }
        except Exception as e:
            current_app.logger.warning(f"Error getting file info: {str(e)}")
            return None
    
    async def process_command(self, user_message):
        """
        Process user command and execute corresponding actions
        """
        try:
            # Start test execution logging
            self.test_logger.start_execution(f"Processing command: {user_message[:50]}...")
            
            # Get list of available files
            all_files = self.file_service.get_files()
            
            # Log directory and file information
            self.test_logger.log_directory_info({
                'white_directories': self.file_service.white_dirs,
                'total_files': len(all_files)
            })
            
            # Check if we have any files
            if not all_files:
                self.test_logger.end_execution()
                return {
                    'response': "No files available in the allowed directories.",
                    'files': []
                }
            
            # Limit the number of files in prompt
            files = all_files[:self.max_files_in_prompt]
            if len(all_files) > self.max_files_in_prompt:
                current_app.logger.warning(
                    f"Number of files ({len(all_files)}) exceeds maximum allowed in prompt ({self.max_files_in_prompt}). "
                    "Only first 5 files will be included."
                )
            
            # Get base directory from the first file's path
            base_dir = os.path.dirname(files[0]['path']) if 'path' in files[0] else self.file_service.white_dirs[0]
            
            # Combine everything into the prompt
            prompt = self.prompt_service.combine_prompt(user_message, files)

            print("==========prompt==========")
            print(prompt)
            print("==========prompt==========")
            
            # Log prompt information
            self.test_logger.log_prompt(prompt, {
                'user_message': user_message,
                'files_in_prompt': len(files)
            })
            
            # Get response from ChatGPT
            llm_response = await self.chat_service.get_response(prompt)
            print("==========llm_response==========")
            print(llm_response)
            print("==========llm_response==========")
            
            # Log LLM response
            self.test_logger.log_llm_response(llm_response)
            
            # End test execution logging
            self.test_logger.end_execution()
            
            return {
                'response': llm_response,
                'files': [self._format_file_info(f['path']) for f in files if f.get('path')]
            }
            
        except Exception as e:
            current_app.logger.error(f"Error processing command: {str(e)}", exc_info=True)
            self.test_logger.log_error(str(e))
            self.test_logger.end_execution()
            return {
                'response': f"Error processing command: {str(e)}",
                'files': []
            } 