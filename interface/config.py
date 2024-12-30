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
        
        # OpenAI configuration
        app.config['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
        
        # Load platform configurations
        self._load_platform_config(app)
        
        # Load application configurations
        self._load_app_config(app)
    
    def _load_platform_config(self, app):
        """Load platform-level configurations"""
        # Logging configuration
        logging_config = os.path.join('shared', 'config', 'logging', 'logging.ini')
        if os.path.exists(logging_config):
            import configparser
            config = configparser.ConfigParser()
            config.read(logging_config)
            if config.has_section('Logging'):
                app.config['MAX_LOG_SIZE'] = config.getint('Logging', 'max_size', fallback=10 * 1024 * 1024)
                app.config['LOG_BACKUP_COUNT'] = config.getint('Logging', 'backup_count', fallback=10)
        else:
            app.config['MAX_LOG_SIZE'] = 10 * 1024 * 1024  # 10MB
            app.config['LOG_BACKUP_COUNT'] = 10
        
        # Elasticsearch configuration
        # First load from config file
        es_config = os.path.join('shared', 'config', 'elasticsearch', 'elasticsearch.ini')
        if os.path.exists(es_config):
            import configparser
            config = configparser.ConfigParser()
            config.read(es_config)
            if config.has_section('Elasticsearch'):
                app.config['ELASTICSEARCH_ENABLED'] = config.getboolean('Elasticsearch', 'enabled', fallback=False)
                app.config['ELASTICSEARCH_HOST'] = config.get('Elasticsearch', 'host', fallback='localhost')
                app.config['ELASTICSEARCH_PORT'] = config.getint('Elasticsearch', 'port', fallback=9200)
                app.config['ELASTICSEARCH_INDEX'] = config.get('Elasticsearch', 'index', fallback='fileapp')
                app.config['ELASTICSEARCH_SCHEME'] = config.get('Elasticsearch', 'scheme', fallback='http')
        
        # Then override with environment variables if they exist
        app.config['ELASTICSEARCH_ENABLED'] = os.getenv('ELASTICSEARCH_ENABLED', 'false').lower() == 'true'
        if os.getenv('ELASTICSEARCH_HOST'):
            app.config['ELASTICSEARCH_HOST'] = os.getenv('ELASTICSEARCH_HOST')
        if os.getenv('ELASTICSEARCH_PORT'):
            app.config['ELASTICSEARCH_PORT'] = int(os.getenv('ELASTICSEARCH_PORT'))
        if os.getenv('ELASTICSEARCH_INDEX'):
            app.config['ELASTICSEARCH_INDEX'] = os.getenv('ELASTICSEARCH_INDEX')
        if os.getenv('ELASTICSEARCH_SCHEME'):
            app.config['ELASTICSEARCH_SCHEME'] = os.getenv('ELASTICSEARCH_SCHEME')
    
    def _load_app_config(self, app):
        """Load application-specific configurations"""
        import configparser
        import os
        
        config = configparser.ConfigParser()
        
        # Load base configuration
        base_config_path = os.path.join('AutoFileManagement', 'config', 'base.ini')
        if os.path.exists(base_config_path):
            config.read(base_config_path)
            
        # Load environment specific configuration
        env = os.getenv('FLASK_ENV', 'development')
        env_config_path = os.path.join('AutoFileManagement', 'config', f'{env}.ini')
        if os.path.exists(env_config_path):
            config.read(env_config_path)
            
        # Load auto file configuration
        autofile_config_path = os.path.join('AutoFileManagement', 'config', 'autofile.ini')
        if os.path.exists(autofile_config_path):
            config.read(autofile_config_path)
            
            # Load directories configuration
            if config.has_section('Directories'):
                white_dirs = []
                for key, value in config.items('Directories'):
                    if key.startswith('dir_'):
                        # Expand user path (e.g. ~/Documents)
                        expanded_path = os.path.expanduser(value)
                        white_dirs.append(expanded_path)
                app.config['WHITE_DIRECTORIES'] = white_dirs
            
            # Load file types configuration
            if config.has_section('FileTypes'):
                file_types = {}
                for key, value in config.items('FileTypes'):
                    file_types[key] = [ext.strip() for ext in value.split(',')]
                app.config['ALLOWED_FILE_TYPES'] = file_types
            
            # Load limits configuration
            if config.has_section('Limits'):
                if config.has_option('Limits', 'max_processable_file_size'):
                    app.config['MAX_PROCESSABLE_FILE_SIZE'] = config.getint('Limits', 'max_processable_file_size')
                if config.has_option('Limits', 'max_files_in_prompt'):
                    app.config['MAX_FILES_IN_PROMPT'] = config.getint('Limits', 'max_files_in_prompt')
            
            # Load file opening configuration
            if config.has_section('FileOpening'):
                if config.has_option('FileOpening', 'preview_enabled'):
                    app.config['PREVIEW_ENABLED'] = config.getboolean('FileOpening', 'preview_enabled')
                if config.has_option('FileOpening', 'max_preview_size'):
                    app.config['MAX_PREVIEW_SIZE'] = config.getint('FileOpening', 'max_preview_size')
            
            # Load OpenAI configuration
            if config.has_section('OpenAI'):
                if config.has_option('OpenAI', 'enabled'):
                    app.config['OPENAI_ENABLED'] = config.getboolean('OpenAI', 'enabled')
                if config.has_option('OpenAI', 'model'):
                    app.config['OPENAI_MODEL'] = config.get('OpenAI', 'model')
                if config.has_option('OpenAI', 'temperature'):
                    app.config['OPENAI_TEMPERATURE'] = config.getfloat('OpenAI', 'temperature')
                if config.has_option('OpenAI', 'max_prompt_tokens'):
                    app.config['MAX_PROMPT_TOKENS'] = config.getint('OpenAI', 'max_prompt_tokens')