import os
from dotenv import load_dotenv

class Config:
    """Configuration class for the application"""
    
    def __init__(self):
        # Force reload environment variables
        load_dotenv(override=True)
        
    def init_app(self, app):
        """Initialize application configuration
        
        Args:
            app: Flask application instance
        """
        # Load configuration from environment variables
        app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
        app.config['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
        
        # Load platform configurations
        self._load_platform_config(app)
        
        # Load AutoFileManagement configurations
        from AutoFileManagement.configs import AutoFileManagementConfig, AutoFileOpeningConfig
        
        # Initialize application level config
        app.logger.debug('Loading AutoFileManagement configurations...')
        auto_file_config = AutoFileManagementConfig()
        auto_file_config.init_app(app)
        
        # Initialize module level config
        app.logger.debug('Loading AutoFileOpening configurations...')
        file_opening_config = AutoFileOpeningConfig()
        file_opening_config.init_app(app)
        
        app.logger.info('All configurations loaded successfully')
    
    def _load_platform_config(self, app):
        """Load platform-level configurations"""
        # Load main platform configuration
        platform_config = os.path.join('shared', 'configs', 'config.ini')
        if os.path.exists(platform_config):
            import configparser
            config = configparser.ConfigParser()
            config.read(platform_config)
            
            # Load App section
            if config.has_section('App'):
                app.config['HOST'] = config.get('App', 'HOST', fallback='0.0.0.0')
                app.config['PORT'] = config.getint('App', 'PORT')
                app.config['DEBUG'] = config.getboolean('App', 'DEBUG', fallback=False)
                app.config['LOG_LEVEL'] = config.get('App', 'LOG_LEVEL', fallback='INFO')
            
            # Load Paths section
            if config.has_section('Paths'):
                app.config['LOG_DIR'] = config.get('Paths', 'LOG_DIR', fallback='shared/logs')
                
                # Ensure directories exist
                for dir_path in [app.config['LOG_DIR']]:
                    os.makedirs(dir_path, exist_ok=True)
        
        # Load logging configuration (separate file for logging specifics)
        logging_config = os.path.join('shared', 'configs', 'logging.ini')
        if os.path.exists(logging_config):
            config = configparser.ConfigParser()
            config.read(logging_config)
            if config.has_section('Logging'):
                app.config['LOG_FILE_LEVEL'] = config.get('Logging', 'FILE_LEVEL')
                app.config['LOG_CONSOLE_LEVEL'] = config.get('Logging', 'CONSOLE_LEVEL')
                app.config['MAX_LOG_SIZE'] = config.getint('Logging', 'MAX_SIZE')
                app.config['LOG_BACKUP_COUNT'] = config.getint('Logging', 'BACKUP_COUNT')
