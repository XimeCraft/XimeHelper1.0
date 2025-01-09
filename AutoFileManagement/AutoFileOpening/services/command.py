from .chat import ChatService
from .prompt import PromptService
from .file import FileService
from flask import current_app
import os
from datetime import datetime
from interface.test_logger import TestLogger
import json

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
    
    def process_command(self, user_message):
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

            # Log prompt information
            self.test_logger.log_prompt(prompt, {
                'user_message': user_message,
                'files_in_prompt': len(files)
            })
            
            # Get response from ChatGPT
            llm_response = self.chat_service.get_response(prompt)
            # llm_response = """{"operation": "open", "filename": "test1.txt"}"""
            print("==========llm_response==========")
            print(llm_response)
            print("==========llm_response==========")
            
            # Log LLM response
            self.test_logger.log_llm_response(llm_response)

            response = None
            try:

                if llm_response != "No matching files found.":
                    # Parse JSON response
                    try:
                        response_data = json.loads(llm_response.replace("'", '"'))
                        operation = response_data['operation']
                        file_name = response_data['filename']
                        print("==========response_data==========")
                        print(response_data)
                        print(operation)
                        print(file_name)
                        print("==========response_data==========")
                    except json.JSONDecodeError:
                        # Fallback to old format parsing
                        parts = llm_response.split(', filename: ')
                        operation = parts[0].split('operation: ')[1].strip()
                        file_name = parts[1].strip()
                    
                    # Convert file name to full path
                    file_path = os.path.join(base_dir, file_name)
                    
                    # Verify the file exists
                    if not os.path.exists(file_path):
                        raise FileNotFoundError(f"File not found: {file_name}")
                    
                    # Get detailed file information
                    file_info = self._format_file_info(file_path)
                    
                    if operation == 'close':
                        self.file_service.close_specific_file(file_path)
                        if file_info:
                            response = f"Closing file:<br>" + \
                                     f"Name: {file_info['name']}<br>" + \
                                     f"Type: {file_info['type']}<br>" + \
                                     f"Path: {file_info['path']}"
                        else:
                            response = f"Closing file: {file_path}"
                    elif operation == 'open':
                        self.file_service.open_file(file_path)
                        if file_info:
                            response = f"Opening file:<br>" + \
                                     f"Name: {file_info['name']}<br>" + \
                                     f"Type: {file_info['type']}<br>" + \
                                     f"Size: {file_info['size']}<br>" + \
                                     f"Modified: {file_info['modified']}<br>" + \
                                     f"Path: {file_info['path']}"
                        else:
                            response = f"Opening file: {file_path}"
                else:
                    response = llm_response
            except Exception as e:
                current_app.logger.warning(f"Failed to open file: {str(e)}")
                response = f"Failed to open file: {str(e)}"

            # End test execution logging
            self.test_logger.end_execution()

            return {
                'response': response,
                'files': all_files  # Return all files to frontend
            }
            
        except Exception as e:
            # Handle errors appropriately
            current_app.logger.error(f"Error in CommandService: {str(e)}", exc_info=True)
            # Make sure to end execution logging even on error
            if hasattr(self, 'test_logger'):
                self.test_logger.end_execution()
            return {
                'error': str(e),
                'response': "Sorry, I encountered an error processing your command.",
                'files': []
            } 