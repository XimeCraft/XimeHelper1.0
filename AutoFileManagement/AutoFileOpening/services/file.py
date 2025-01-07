import os
from pathlib import Path
from flask import current_app
import fnmatch
import subprocess
from .apple_script import AppleScriptService
import time

class FileService:
    def __init__(self):
        self.white_dirs = current_app.config.get('AUTO_FILE_OPENING_WHITE_DIRS', [])
        self.file_types = current_app.config.get('AUTO_FILE_OPENING_FILE_TYPES', {})
        self.max_file_size = current_app.config.get('AUTO_FILE_OPENING_MAX_PROCESSABLE_SIZE', float('inf'))
        self.app_mapping = current_app.config.get('AUTO_FILE_OPENING_APP_MAPPING', {})
        
        # Validate and expand all directory paths
        self.white_dirs = [os.path.expanduser(os.path.expandvars(d)) for d in self.white_dirs]
        # Filter out non-existent directories
        self.white_dirs = [d for d in self.white_dirs if os.path.exists(d)]
        
        if not self.white_dirs:
            current_app.logger.warning("No valid directories found in whitelist")

    def _get_app_name(self, file_path):
        """Get the application name for a given file path based on its extension"""
        ext = os.path.splitext(file_path)[1].lower().lstrip('.')
        return self.app_mapping.get(ext, '')

    def _verify_file_path(self, file_path):
        """Verify file path exists and is in whitelist"""
        file_path = os.path.expanduser(os.path.expandvars(file_path))
        file_path = os.path.abspath(file_path)
        
        # Verify file is in white list directory
        if not any(os.path.commonpath([file_path, os.path.abspath(white_dir)]) == os.path.abspath(white_dir) 
                  for white_dir in self.white_dirs):
            raise ValueError("File path is not in white list directories")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        return file_path

    def open_file(self, file_path):
        """Open file with default application if it's in white list directory"""
        try:
            file_path = self._verify_file_path(file_path)
            current_app.logger.info(f"Opening file: {file_path}")
            
            if not os.access(file_path, os.R_OK):
                raise PermissionError(f"No permission to read file: {file_path}")

            import platform
            if platform.system() == 'Darwin':       # macOS
                os.system(f'open "{file_path}"')
                time.sleep(0.2)  # Reduced from 0.5 to 0.2
            elif platform.system() == 'Windows':    # Windows
                os.system(f'start "" "{file_path}"')
            else:                                   # Linux
                os.system(f'xdg-open "{file_path}"')
                
        except Exception as e:
            current_app.logger.error(f"Error opening file {file_path}: {e}")
            raise

    def _get_process_info(self, file_path):
        """Get process info for an open file using lsof"""
        try:
            result = subprocess.run(['lsof', str(file_path)], 
                                capture_output=True, 
                                text=True)
            if result.stdout:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                processes = [line.split()[0] for line in lines]
                current_app.logger.debug(f"Found processes for {file_path}: {processes}")
                return processes
            return []
        except Exception as e:
            current_app.logger.error(f"Error getting process info: {e}")
            return []

    def is_file_open(self, file_path):
        """Check if a file is currently open using AppleScript"""
        file_path = self._verify_file_path(file_path)
        file_name = os.path.basename(file_path)
        
        # Use AppleScript to check if file is open
        result = AppleScriptService.get_open_processes(file_name)
        
        if result:
            current_app.logger.info(f"File {file_name} is open in: {result}")
            return True
        return False

    def close_specific_file(self, file_path):
        """Close a specific file while keeping others open"""
        file_path = self._verify_file_path(file_path)
        file_name = os.path.basename(file_path)
        
        # First check if file is open
        if not self.is_file_open(file_path):
            current_app.logger.info(f"File is not open: {file_path}")
            return True  # Return True as the file is already closed
        
        # Get the process that has the file open
        result = AppleScriptService.find_window_process(file_name)
        print("============result==========")
        print(result)   
        print("===========result===========")

        
        if not result or result == "{}":
            current_app.logger.warning(f"No process found with open file: {file_name}")
            return False
        
        process_info = result.strip("{}").split(",")
        process_name = process_info[0].strip()
        
        current_app.logger.info(f"Found file in process: {process_name}")
        
        # Save and close the specific window
        success = AppleScriptService.save_and_close_window(process_name, file_name)
        
        if success:
            current_app.logger.info(f"Successfully closed {file_name}")
        else:
            current_app.logger.warning(f"Failed to close {file_name}")
        return success

    def get_files(self, directory=None, file_type=None):
        """
        Get list of files from white list directories
        
        Args:
            directory (str, optional): Specific directory to search in
            file_type (str, optional): Type of files to search for
            
        Returns:
            list: List of dictionaries containing file information
            Each dictionary contains:
                - name: File name
                - path: Full path to the file
                - type: File extension (without dot)
                - size: File size in bytes
                - directory: Base directory containing the file
        """
        files = []
        
        try:
            if directory:
                directory = os.path.expanduser(os.path.expandvars(directory))
                search_dirs = [directory] if directory in self.white_dirs else []
            else:
                search_dirs = self.white_dirs

            for base_dir in search_dirs:
                if not os.path.exists(base_dir):
                    current_app.logger.warning(f"Directory not found: {base_dir}")
                    continue

                for root, _, filenames in os.walk(base_dir):
                    # Skip hidden directories
                    if any(part.startswith('.') for part in Path(root).parts):
                        continue

                    for filename in filenames:
                        try:
                            # Skip hidden files
                            if filename.startswith('.'):
                                continue

                            file_path = os.path.join(root, filename)
                            
                            # Skip if file doesn't exist or is not accessible
                            if not os.path.exists(file_path) or not os.access(file_path, os.R_OK):
                                continue
                                
                            file_ext = Path(filename).suffix.lower()
                            
                            # Check if file type matches (if specified)
                            if file_type and not self._is_white_type(file_ext, file_type):
                                continue

                            # Check file size
                            try:
                                file_size = os.path.getsize(file_path)
                                if file_size > self.max_file_size:
                                    continue
                            except OSError as e:
                                current_app.logger.warning(f"Could not get size for file {file_path}: {e}")
                                continue

                            files.append({
                                'name': filename,
                                'path': file_path,
                                'type': file_ext[1:] if file_ext else '',  # Remove the dot
                                'size': file_size,
                                'directory': base_dir
                            })
                        except Exception as e:
                            current_app.logger.warning(f"Error processing file {filename}: {e}")
                            continue
                            
        except Exception as e:
            current_app.logger.error(f"Error in get_files: {e}")
            return []
            
        return files
    
    def _is_white_type(self, extension, file_type):
        """Check if file extension is in white list for given type"""
        white_extensions = self.file_types.get(file_type, [])
        return extension.lower() in white_extensions
    
    def search_files(self, pattern, directory=None):
        """
        Search for files matching pattern in white list directories
        
        Args:
            pattern (str): Search pattern (supports wildcards)
            directory (str, optional): Specific directory to search in
            
        Returns:
            list: List of matching files
        """
        try:
            all_files = self.get_files(directory)
            return [f for f in all_files 
                    if fnmatch.fnmatch(f['name'].lower(), pattern.lower())]
        except Exception as e:
            current_app.logger.error(f"Error in search_files: {e}")
            return []