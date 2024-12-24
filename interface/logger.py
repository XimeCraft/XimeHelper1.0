import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

def setup_logger(app):
    """
    Setup application logging system
    
    Args:
        app: Flask application instance
    """
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Set log filename (by date)
    log_file = os.path.join(log_dir, f'ximehelper_{datetime.now().strftime("%Y%m%d")}.log')
    
    # Set log format
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )
    
    # File handler (using configured size and backup count)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=app.config.get('MAX_LOG_SIZE', 10485760),
        backupCount=app.config.get('LOG_BACKUP_COUNT', 10)
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.WARNING)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.WARNING)
    
    # Configure Flask application logger
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(logging.WARNING)
    
    # Configure Werkzeug logger
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.addHandler(file_handler)
    werkzeug_logger.addHandler(console_handler)
    werkzeug_logger.setLevel(logging.WARNING)
    
    # Configure SQLAlchemy logger (if using database)
    sqlalchemy_logger = logging.getLogger('sqlalchemy.engine')
    sqlalchemy_logger.addHandler(file_handler)
    sqlalchemy_logger.addHandler(console_handler)
    sqlalchemy_logger.setLevel(logging.WARNING)
    
    # Create a general logger for the entire application
    app.config['LOGGER'] = app.logger
    
    app.logger.info('Logger initialized successfully') 