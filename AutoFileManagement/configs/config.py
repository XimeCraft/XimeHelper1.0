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

        # Load OpenAI configuration
        self.openai_enabled = self.config.getboolean('OpenAI', 'ENABLED')
        self.openai_model = self.config.get('OpenAI', 'MODEL') 
        self.openai_temperature = self.config.getfloat('OpenAI', 'TEMPERATURE')
        self.openai_max_prompt_tokens = self.config.getint('OpenAI', 'MAX_PROMPT_TOKENS')

        # Load Ollama configuration
        self.ollama_enabled = self.config.getboolean('Ollama', 'ENABLED')
        self.ollama_model = self.config.get('Ollama', 'MODEL')
        self.ollama_temperature = self.config.getfloat('Ollama', 'TEMPERATURE')
        self.ollama_max_prompt_tokens = self.config.getint('Ollama', 'MAX_PROMPT_TOKENS')
        self.ollama_base_url = self.config.get('Ollama', 'BASE_URL', fallback='http://localhost:11434')

    def init_app(self, app):
        """Initialize Flask application with AutoFileManagement configurations
        
        Args:
            app: Flask application instance
        """
        # App configuration
        app.config['AUTO_FILE_DEBUG'] = self.debug

        # Paths configuration
        app.config['AUTO_FILE_BASE_DIR'] = self.base_dir
    
        # OpenAI configuration
        app.config['AUTO_FILE_OPENAI_ENABLED'] = self.openai_enabled
        app.config['AUTO_FILE_OPENAI_MODEL'] = self.openai_model
        app.config['AUTO_FILE_OPENAI_TEMPERATURE'] = self.openai_temperature
        app.config['AUTO_FILE_MAX_PROMPT_TOKENS'] = self.openai_max_prompt_tokens
        
        # Ollama configuration
        app.config['AUTO_FILE_OLLAMA_ENABLED'] = self.ollama_enabled
        app.config['AUTO_FILE_OLLAMA_MODEL'] = self.ollama_model
        app.config['AUTO_FILE_OLLAMA_TEMPERATURE'] = self.ollama_temperature
        app.config['AUTO_FILE_OLLAMA_MAX_PROMPT_TOKENS'] = self.ollama_max_prompt_tokens
        app.config['AUTO_FILE_OLLAMA_URL'] = self.ollama_base_url
