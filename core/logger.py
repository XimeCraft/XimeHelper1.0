import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
import configparser
import sys

class LogManager:
    """Logging manager for handling application logging"""
    
    def __init__(self):
        """Initialize LogManager with configuration"""
        self.config = configparser.RawConfigParser()
        config_path = os.path.join(os.path.dirname(__file__), '../shared/configs/logging.ini')
        self.config.read(config_path)
    
    def setup_logger(self, app):
        """Setup application logging system"""
        # Ensure log directory exists
        log_dir = os.path.join(os.path.dirname(__file__), '../logs')
        os.makedirs(log_dir, exist_ok=True)
        
        # Get log format settings from config
        log_format = self.config.get('Format', 'LOG_FORMAT')
        date_format = self.config.get('Format', 'DATE_FORMAT')
        file_name_format = self.config.get('Format', 'FILE_NAME_FORMAT')
            
        # Set log filename
        log_file = os.path.join(log_dir, datetime.now().strftime(file_name_format))
        
        # Get logging levels
        file_level = getattr(logging, self.config.get('Logging', 'FILE_LEVEL'))
        console_level = getattr(logging, self.config.get('Logging', 'CONSOLE_LEVEL'))
        
        # Create formatter
        formatter = logging.Formatter(log_format, date_format)
        
        # Setup file handler
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=self.config.getint('Logging', 'MAX_SIZE'),
            backupCount=self.config.getint('Logging', 'BACKUP_COUNT')
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(file_level)
        
        # Setup console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(console_level)
        
        # Configure root logger to control all logging
        root_logger = logging.getLogger()
        root_logger.handlers = []  # Remove any existing handlers
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        root_logger.setLevel(min(file_level, console_level))
        
        # Configure Flask application logger
        app.logger.handlers = []
        
        # Configure specific loggers
        loggers_to_configure = [
            'werkzeug',
            'hypercorn.error',
            'hypercorn.access',
            'interface.app',
            'asgiref.sync'
        ]
        
        for logger_name in loggers_to_configure:
            logger = logging.getLogger(logger_name)
            logger.handlers = []
            logger.propagate = True  # Let the root logger handle everything
        
        # Store logger in app config
        app.config['LOGGER'] = app.logger
        
        # Disable Hypercorn access logs
        logging.getLogger('hypercorn.access').disabled = True
        
        # Log initialization only to file
        file_handler.handle(
            logging.LogRecord(
                'LogManager', logging.INFO, '', 0,
                'Logger initialized successfully', (), None
            )
        ) 