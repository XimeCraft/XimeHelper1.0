"""
Configuration manager for AutoFileOpening module
"""
import os
import configparser

class AutoFileOpeningConfig:
    """Configuration manager for AutoFileOpening module"""
    
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.load_config()
    
    def load_config(self):
        """Load module specific configuration"""
        config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
            
        self.config.read(config_path)
        
        # Load white directories
        self.white_dirs = []
        for key, value in self.config.items('WhiteDirectories'):
            if key.startswith('dir_'):
                expanded_path = os.path.expanduser(value)
                self.white_dirs.append(expanded_path.strip())
        
        # Load file types configuration
        self.file_types = {}
        for key, value in self.config.items('FileTypes'):
            # Split by comma and clean up each extension
            extensions = [ext.strip() for ext in value.split(',')]
            self.file_types[key.upper()] = extensions
        
        # Load limits configuration
        self.max_processable_file_size = self.config.getint(
            'Limits', 
            'MAX_PROCESSABLE_FILE_SIZE',
            fallback=10 * 1024 * 1024  # 10MB default
        )
        self.max_files_in_prompt = self.config.getint(
            'Limits', 
            'MAX_FILES_IN_PROMPT',
            fallback=10
        )
    
    def init_app(self, app):
        """Initialize Flask application with module configurations
        
        Args:
            app: Flask application instance
        """
        # White directories configuration
        app.config['AUTO_FILE_OPENING_WHITE_DIRS'] = self.white_dirs
        
        # File types configuration
        app.config['AUTO_FILE_OPENING_FILE_TYPES'] = self.file_types
 
        # Create a set of all allowed extensions for easy lookup
        all_extensions = set()
        for extensions in self.file_types.values():
            all_extensions.update(extensions)
        app.config['AUTO_FILE_OPENING_ALLOWED_EXTENSIONS'] = all_extensions
        
        # Limits configuration
        app.config['AUTO_FILE_OPENING_MAX_PROCESSABLE_SIZE'] = self.max_processable_file_size
        app.config['AUTO_FILE_OPENING_MAX_FILES_IN_PROMPT'] = self.max_files_in_prompt
        
        # Ensure white directories exist
        for dir_path in self.white_dirs:
            if dir_path:
                os.makedirs(dir_path, exist_ok=True) 