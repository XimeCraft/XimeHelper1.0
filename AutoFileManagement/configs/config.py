import os
import configparser

class AutoFileManagementConfig:
    """Configuration manager for AutoFileManagement platform"""
    
    def __init__(self):
        self.config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
        self.load_config()
        
    def load_config(self):
        """Load platform configuration"""
        config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
        if os.path.exists(config_path):
            self.config.read(config_path)
            
        # Load environment variables
        self.debug = self.config.getboolean('App', 'DEBUG', fallback=True)
        self.env = self.config.get('App', 'ENV', fallback='development')
        
        # Load paths
        self.base_dir = self.config.get('Paths', 'BASE_DIR')
        self.log_dir = self.config.get('Paths', 'LOG_DIR')
        self.data_dir = self.config.get('Paths', 'DATA_DIR')
        
        # Load logging configuration
        self.log_file_level = self.config.get('Logging', 'FILE_LEVEL')
        self.log_console_level = self.config.get('Logging', 'CONSOLE_LEVEL')
        self.log_max_size = self.config.getint('Logging', 'MAX_SIZE')
        self.log_backup_count = self.config.getint('Logging', 'BACKUP_COUNT')
        
        # Load security configuration
        self.secret_key = self.config.get('Security', 'SECRET_KEY')
        
        # Load OpenAI configuration
        self.openai_enabled = self.config.getboolean('OpenAI', 'ENABLED')
        self.openai_model = self.config.get('OpenAI', 'MODEL') 
        self.openai_temperature = self.config.getfloat('OpenAI', 'TEMPERATURE')
        self.openai_max_prompt_tokens = self.config.getint('OpenAI', 'MAX_PROMPT_TOKENS')

    def get_module_config_path(self, module_name):
        """Get configuration path for a specific module"""
        return os.path.join(
            os.path.dirname(__file__),
            module_name,
            'settings',
            'config.ini'
        ) 

    def init_app(self, app):
        """Initialize Flask application with AutoFileManagement configurations
        
        Args:
            app: Flask application instance
        """
        # App configuration
        app.config['AUTO_FILE_DEBUG'] = self.debug
        app.config['AUTO_FILE_ENV'] = self.env
        
        # Paths configuration
        app.config['AUTO_FILE_BASE_DIR'] = self.base_dir
        app.config['AUTO_FILE_LOG_DIR'] = self.log_dir
        app.config['AUTO_FILE_DATA_DIR'] = self.data_dir
        
        # Logging configuration
        app.config['AUTO_FILE_LOG_FILE_LEVEL'] = self.log_file_level
        app.config['AUTO_FILE_LOG_CONSOLE_LEVEL'] = self.log_console_level
        app.config['AUTO_FILE_LOG_MAX_SIZE'] = self.log_max_size
        app.config['AUTO_FILE_LOG_BACKUP_COUNT'] = self.log_backup_count
        
        # Security configuration
        if not app.config.get('SECRET_KEY'):  # Only set if not already set by platform config
            app.config['SECRET_KEY'] = self.secret_key
        
        # OpenAI configuration
        app.config['AUTO_FILE_OPENAI_ENABLED'] = self.openai_enabled
        app.config['AUTO_FILE_OPENAI_MODEL'] = self.openai_model
        app.config['AUTO_FILE_OPENAI_TEMPERATURE'] = self.openai_temperature
        app.config['AUTO_FILE_MAX_PROMPT_TOKENS'] = self.openai_max_prompt_tokens
        
        # Ensure required directories exist
        for dir_path in [self.log_dir, self.data_dir]:
            if dir_path:
                os.makedirs(dir_path, exist_ok=True) 