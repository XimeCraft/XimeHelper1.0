import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-please-change')
    
    # White list directories for file operations
    WHITE_DIRECTORIES = [
        os.path.expanduser('~/Downloads'),     # User's Downloads folder
        os.path.expanduser('~/Projects'),      # User's Projects folder
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'test')  # Local test directory
    ]
    
    # File type white list (optional)
    WHITE_FILE_TYPES = {
        'document': ['.pdf', '.doc', '.docx', '.txt', '.md'],
        'image': ['.jpg', '.jpeg', '.png', '.gif'],
        'data': ['.csv', '.xlsx', '.json']
    }
    
    # Maximum file size (in bytes, optional)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() in ('true', '1', 't')
    
    # Database Configuration
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///chat.db')
    
    # API
    API_VERSION = 'v1'
    API_PREFIX = f'/api/{API_VERSION}'
    
    @staticmethod
    def init_app(app):
        pass 