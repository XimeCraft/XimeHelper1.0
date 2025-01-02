import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
import configparser

class LogManager:
    """Logging manager for handling application logging"""
    
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.load_config()
        
    def load_config(self):
        """Load logging configuration"""
        # Load platform logging config
        platform_logging = os.path.join('shared', 'configs', 'logging.ini')
        if os.path.exists(platform_logging):
            self.config.read(platform_logging)
    
    def setup_logger(self, app, log_dir=None):
        """Setup application logging system"""
        # Determine log directory
        if log_dir is None:
            log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        
        # Ensure log directory exists
        os.makedirs(log_dir, exist_ok=True)
        
        # Get log format settings
        log_format = '[%(asctime)s] %(levelname)s in %(module)s.%(funcName)s:%(lineno)d: %(message)s'
        date_format = '%Y-%m-%d %H:%M:%S'
        file_name_format = 'ximehelper_%Y%m%d.log'
            
        # Set log filename
        log_file = os.path.join(log_dir, datetime.now().strftime(file_name_format))
        
        # Get logging levels
        file_level = getattr(logging, self.config.get('Logging', 'file_level', fallback='DEBUG'))
        
        # Create formatter
        formatter = logging.Formatter(log_format, date_format)
        
        # Setup file handler
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=self.config.getint('Logging', 'max_size', fallback=10485760),
            backupCount=self.config.getint('Logging', 'backup_count', fallback=10)
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(file_level)
        
        # Configure Flask application logger
        app.logger.handlers = []  # Remove default handlers
        app.logger.addHandler(file_handler)
        app.logger.setLevel(file_level)
        
        # Configure Werkzeug logger
        werkzeug_logger = logging.getLogger('werkzeug')
        werkzeug_logger.handlers = []  # Remove default handlers
        werkzeug_logger.addHandler(file_handler)
        werkzeug_logger.setLevel(logging.WARNING)  # Only log warnings and errors for Werkzeug
        
        # Store logger in app config
        app.config['LOGGER'] = app.logger
        
        app.logger.info('Logger initialized successfully') 