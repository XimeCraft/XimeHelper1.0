import os
from pathlib import Path
from flask import current_app
import fnmatch

class FileService:
    def __init__(self):
        self.white_dirs = current_app.config['WHITE_DIRECTORIES']
        self.white_types = current_app.config.get('WHITE_FILE_TYPES', {})
        self.max_file_size = current_app.config.get('MAX_FILE_SIZE', float('inf'))

    def get_files(self, directory=None, file_type=None):
        """
        Get list of files from white list directories
        
        Args:
            directory (str, optional): Specific directory to search in
            file_type (str, optional): Type of files to search for
            
        Returns:
            list: List of dictionaries containing file information
        """
        files = []
        search_dirs = [directory] if directory in self.white_dirs else self.white_dirs

        for base_dir in search_dirs:
            if not os.path.exists(base_dir):
                continue

            for root, _, filenames in os.walk(base_dir):
                # Skip hidden directories
                if any(part.startswith('.') for part in Path(root).parts):
                    continue

                for filename in filenames:
                    # Skip hidden files
                    if filename.startswith('.'):
                        continue

                    file_path = os.path.join(root, filename)
                    file_ext = Path(filename).suffix.lower()
                    
                    # Check if file type matches (if specified)
                    if file_type and not self._is_white_type(file_ext, file_type):
                        continue

                    # Check file size
                    file_size = os.path.getsize(file_path)
                    if file_size > self.max_file_size:
                        continue

                    # Get relative path from base directory
                    rel_path = os.path.relpath(file_path, base_dir)
                    
                    files.append({
                        'name': filename,
                        'path': file_path,
                        'relative_path': rel_path,
                        'type': file_ext[1:] if file_ext else '',  # Remove the dot
                        'size': file_size,
                        'directory': base_dir
                    })

        return files

    def _is_white_type(self, extension, file_type):
        """Check if file extension is in white list for given type"""
        white_extensions = self.white_types.get(file_type, [])
        return extension.lower() in white_extensions

    def open_file(self, file_path):
        """
        Open file with default application if it's in white list directory
        
        Args:
            file_path (str): Path to file
        """
        # Verify file is in white list directory
        if not any(os.path.commonpath([file_path, white_dir]) == white_dir 
                  for white_dir in self.white_dirs):
            raise ValueError("File path is not in white list directories")

        if os.path.exists(file_path):
            import platform
            if platform.system() == 'Darwin':       # macOS
                os.system(f'open "{file_path}"')
            elif platform.system() == 'Windows':    # Windows
                os.system(f'start "" "{file_path}"')
            else:                                   # Linux
                os.system(f'xdg-open "{file_path}"')

    def search_files(self, pattern, directory=None):
        """
        Search for files matching pattern in white list directories
        
        Args:
            pattern (str): Search pattern (supports wildcards)
            directory (str, optional): Specific directory to search in
            
        Returns:
            list: List of matching files
        """
        all_files = self.get_files(directory)
        return [f for f in all_files 
                if fnmatch.fnmatch(f['name'].lower(), pattern.lower())]