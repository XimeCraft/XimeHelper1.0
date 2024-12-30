import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from elasticsearch import Elasticsearch
from logging import LogRecord
import json

class ElasticsearchHandler(logging.Handler):
    def __init__(self, host, port, index, scheme):
        super().__init__()
        self.es = None
        self.index = f"{index}-{datetime.now().strftime('%Y.%m.%d')}"
        self.connection_params = {
            'host': host,
            'port': port,
            'scheme': scheme
        }
        self._connect_to_elasticsearch()

    def _connect_to_elasticsearch(self):
        try:
            self.es = Elasticsearch(
                [self.connection_params],
                verify_certs=False,
                retry_on_timeout=True,
                max_retries=3,
                timeout=30
            )
            # Test the connection and create index if not exists
            if not self.es.ping():
                raise ConnectionError("Could not ping Elasticsearch server")
            
            # Create index with mapping if it doesn't exist
            if not self.es.indices.exists(index=self.index):
                mapping = {
                    "mappings": {
                        "properties": {
                            "timestamp": {"type": "date"},
                            "level": {"type": "keyword"},
                            "module": {"type": "keyword"},
                            "message": {"type": "text"}
                        }
                    }
                }
                self.es.indices.create(index=self.index, body=mapping)
            
            print(f"Successfully connected to Elasticsearch at {self.connection_params['host']}:{self.connection_params['port']}")
        except Exception as e:
            print(f"Failed to initialize Elasticsearch: {str(e)}")
            self.es = None

    def emit(self, record: LogRecord):
        if not self.es:
            self._connect_to_elasticsearch()
            if not self.es:
                return
            
        try:
            msg = self.format(record)
            doc = {
                'timestamp': datetime.now().isoformat(),
                'level': record.levelname,
                'module': record.module,
                'message': msg,
                'function': record.funcName,
                'line_number': record.lineno,
                'path': record.pathname,
                'thread': record.threadName,
                'process': record.process
            }
            self.es.index(index=self.index, document=doc)
        except Exception as e:
            print(f"Error sending log to Elasticsearch: {e}")

def setup_logger(app):
    """
    Setup application logging system
    
    Args:
        app: Flask application instance
    """
    # Get log directory from environment variable or use default
    log_dir = os.getenv('LOG_DIR', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs'))
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Set log filename (by date)
    log_file = os.path.join(log_dir, f'ximehelper_{datetime.now().strftime("%Y%m%d")}.log')
    
    # Set detailed log format
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s.%(funcName)s:%(lineno)d: %(message)s'
    )
    
    # File handler with DEBUG level for detailed logging
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=app.config.get('MAX_LOG_SIZE', 10485760),
        backupCount=app.config.get('LOG_BACKUP_COUNT', 10)
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler remains at WARNING level
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.WARNING)
    
    # Setup Elasticsearch handler
    try:
        es_handler = ElasticsearchHandler(
            host=app.config['ELASTICSEARCH_HOST'],
            port=app.config['ELASTICSEARCH_PORT'],
            index=app.config['ELASTICSEARCH_INDEX'],
            scheme=app.config['ELASTICSEARCH_SCHEME']
        )
        es_handler.setFormatter(formatter)
        es_handler.setLevel(logging.INFO)
        
        if es_handler.es:  # Only add handler if connection successful
            app.logger.addHandler(es_handler)
            werkzeug_logger = logging.getLogger('werkzeug')
            werkzeug_logger.addHandler(es_handler)
            sqlalchemy_logger = logging.getLogger('sqlalchemy.engine')
            sqlalchemy_logger.addHandler(es_handler)
            app.logger.info('Elasticsearch logging enabled')
        else:
            app.logger.warning('Elasticsearch logging disabled due to connection failure')
    except Exception as e:
        app.logger.warning(f'Failed to initialize Elasticsearch logging: {str(e)}')
    
    # Configure Flask application logger
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(logging.INFO)
    
    # Configure Werkzeug logger
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.addHandler(file_handler)
    werkzeug_logger.addHandler(console_handler)
    werkzeug_logger.setLevel(logging.INFO)
    
    # Configure SQLAlchemy logger
    sqlalchemy_logger = logging.getLogger('sqlalchemy.engine')
    sqlalchemy_logger.addHandler(file_handler)
    sqlalchemy_logger.addHandler(console_handler)
    sqlalchemy_logger.setLevel(logging.INFO)
    
    # Create a general logger for the entire application
    app.config['LOGGER'] = app.logger
    
    app.logger.info('Logger initialized successfully') 