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

    async def _detect_operation(self, user_message):
        """Detect the operation (open/close) from user message"""
        operation_prompt = self.prompt_service.get_operation_prompt(user_message)
        operation = await self.chat_service.get_response(operation_prompt)
        return operation.strip().lower()

    async def _match_file(self, user_message, files):
        """Match the file from user message"""
        file_prompt = self.prompt_service.get_file_matching_prompt(user_message, files)
        filename = await self.chat_service.get_response(file_prompt)
        return filename.strip().strip('"').strip("'")

    def _handle_open_file(self, file_path):
        """Handle opening a file"""
        file_info = self._format_file_info(file_path)
        self.file_service.open_file(file_path)
        
        if file_info:
            return f"Opening file:<br>" + \
                   f"Name: {file_info['name']}<br>" + \
                   f"Type: {file_info['type']}<br>" + \
                   f"Size: {file_info['size']}<br>" + \
                   f"Modified: {file_info['modified']}<br>" + \
                   f"Path: {file_info['path']}"
        return f"Opening file: {file_path}"

    def _handle_close_file(self, file_path):
        """Handle closing a file"""
        file_info = self._format_file_info(file_path)
        self.file_service.close_file(file_path)
        
        if file_info:
            return f"Closing file:<br>" + \
                   f"Name: {file_info['name']}<br>" + \
                   f"Type: {file_info['type']}<br>" + \
                   f"Path: {file_info['path']}"
        return f"Closing file: {file_path}"
    
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
            
            try:
                # First detect the operation
                operation = await self._detect_operation(user_message)
                if operation not in ['open', 'close']:
                    return {
                        'response': "Sorry, I couldn't understand if you want to open or close a file.",
                        'files': all_files
                    }
                
                # Then match the file
                filename = await self._match_file(user_message, files)
                if filename == "No matching files found.":
                    return {
                        'response': filename,
                        'files': all_files
                    }
                
                # Convert file name to full path
                file_path = os.path.join(base_dir, filename)
                
                # Verify the file exists
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"File not found: {filename}")
                
                # Handle the operation
                if operation == 'open':
                    response = self._handle_open_file(file_path)
                else:  # operation == 'close'
                    response = self._handle_close_file(file_path)
                
            except Exception as e:
                current_app.logger.warning(f"Failed to process file operation: {str(e)}")
                response = f"Failed to process file operation: {str(e)}"

            # End test execution logging
            self.test_logger.end_execution()

            return {
                'response': response,
                'files': all_files
            }
            
        except Exception as e:
            current_app.logger.error(f"Error in CommandService: {str(e)}", exc_info=True)
            if hasattr(self, 'test_logger'):
                self.test_logger.end_execution()
            return {
                'error': str(e),
                'response': "Sorry, I encountered an error processing your command.",
                'files': []
            } 