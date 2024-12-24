import os
import configparser
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration loader for XimeHelper application"""
    
    def __init__(self):
        self.config = {}
        self.config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
        
        if not os.path.exists(self.config_dir):
            raise FileNotFoundError(f"Configuration directory not found: {self.config_dir}")
        
        # Load base configuration
        self.config['base'] = self._load_config_file('base.ini')
        
        # Load feature-specific configurations
        self.config['autofile'] = self._load_config_file('autofile.ini')
        
        self._process_config()
    
    def _load_config_file(self, filename):
        """Load a specific configuration file"""
        config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
        config_path = os.path.join(self.config_dir, filename)
        
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        config.read(config_path)
        return config
    
    def _process_config(self):
        """Process and combine all configuration values"""
        # Load security settings from base config
        self.SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-please-change')
        
        # Load API settings from base config
        self.API_VERSION = self.config['base'].get('API', 'version')
        self.API_PREFIX = self.config['base'].get('API', 'prefix')
        
        # Load logging settings from base config
        self.MAX_LOG_SIZE = self.config['base'].getint('Logging', 'max_log_size')
        self.LOG_BACKUP_COUNT = self.config['base'].getint('Logging', 'log_backup_count')
        
        # Load test logging settings
        base = self.config['base']
        self.TEST_PROMPT_LOGGING = base.getboolean('TestLogging', 'prompt_logging')
        self.TEST_LLM_RESPONSE_LOGGING = base.getboolean('TestLogging', 'llm_response_logging')
        self.TEST_FILE_INFO_LOGGING = base.getboolean('TestLogging', 'file_info_logging')
        self.TEST_DIRECTORY_INFO_LOGGING = base.getboolean('TestLogging', 'directory_info_logging')
        self.TEST_LOCAL_STATE_LOGGING = base.getboolean('TestLogging', 'local_state_logging')
        self.TEST_LOG_FILE = base.get('TestLogging', 'test_log_file')
        self.TEST_LOG_FORMAT = base.get('TestLogging', 'test_log_format')
        
        # Load AutoFile settings
        autofile = self.config['autofile']
        
        # Load directory whitelist
        self.WHITE_DIRECTORIES = []
        i = 1
        while True:
            try:
                dir_path = autofile.get('Directories', f'dir_{i}')
                self.WHITE_DIRECTORIES.append(os.path.expanduser(dir_path))
                i += 1
            except configparser.NoOptionError:
                break
        
        # Load file type whitelist
        self.WHITE_FILE_TYPES = {
            section: [ext.strip() for ext in autofile.get('FileTypes', section).split(',')]
            for section in ['document', 'image', 'data']
        }
        
        # Load file limits
        self.MAX_FILE_SIZE = autofile.getint('Limits', 'max_processable_file_size')
        self.MAX_PREVIEW_SIZE = autofile.getint('FileOpening', 'max_preview_size')
        self.PREVIEW_ENABLED = autofile.getboolean('FileOpening', 'preview_enabled')
        self.MAX_FILES_IN_PROMPT = autofile.getint('Limits', 'max_files_in_prompt')
        
        # Load OpenAI settings
        self.OPENAI_ENABLED = autofile.getboolean('OpenAI', 'enabled')
        self.OPENAI_MODEL = autofile.get('OpenAI', 'model')
        self.OPENAI_TEMPERATURE = autofile.getfloat('OpenAI', 'temperature')
        self.MAX_PROMPT_TOKENS = autofile.getint('OpenAI', 'max_prompt_tokens')
    
    def init_app(self, app):
        """Initialize Flask application with configuration"""
        # Set Flask configuration
        app.config['SECRET_KEY'] = self.SECRET_KEY
        
        # Set logging configuration
        app.config['MAX_LOG_SIZE'] = self.MAX_LOG_SIZE
        app.config['LOG_BACKUP_COUNT'] = self.LOG_BACKUP_COUNT
        
        # Set API configuration
        app.config['API_VERSION'] = self.API_VERSION
        app.config['API_PREFIX'] = self.API_PREFIX
        
        # Set AutoFile configuration
        app.config['WHITE_DIRECTORIES'] = self.WHITE_DIRECTORIES
        app.config['WHITE_FILE_TYPES'] = self.WHITE_FILE_TYPES
        app.config['MAX_FILE_SIZE'] = self.MAX_FILE_SIZE
        app.config['MAX_PREVIEW_SIZE'] = self.MAX_PREVIEW_SIZE
        app.config['PREVIEW_ENABLED'] = self.PREVIEW_ENABLED
        app.config['MAX_FILES_IN_PROMPT'] = self.MAX_FILES_IN_PROMPT
        
        # Set OpenAI configuration
        app.config['OPENAI_ENABLED'] = self.OPENAI_ENABLED
        app.config['OPENAI_MODEL'] = self.OPENAI_MODEL
        app.config['OPENAI_TEMPERATURE'] = self.OPENAI_TEMPERATURE
        app.config['MAX_PROMPT_TOKENS'] = self.MAX_PROMPT_TOKENS