from flask import Flask, render_template, g
from dotenv import load_dotenv
from core.logger import LogManager
from core.config import Config
import time

# Force reload environment variables
load_dotenv(override=True)

def create_app():
    # Force reload environment variables again when creating app
    load_dotenv(override=True)
    
    app = Flask(__name__,
                static_folder='static',
                template_folder='templates')
    
    # Load configuration
    config = Config()
    config.init_app(app)
    
    # Setup logger
    log_manager = LogManager()
    log_manager.setup_logger(app)
    app.logger.info('Starting XimeHelper application...')
    
    # Register blueprints
    try:
        # Import the blueprint
        app.logger.debug('Attempting to import API blueprint...')
        from AutoFileManagement.AutoFileOpening.api import bp as file_bp
        
        # Register the blueprint
        app.logger.debug('Registering API blueprint...')
        app.register_blueprint(file_bp, url_prefix='/api')
        app.logger.info('Successfully registered API blueprint with prefix /api')
        
        # List all registered routes for debugging
        app.logger.debug('Registered routes:')
        for rule in app.url_map.iter_rules():
            app.logger.debug(f'Route: {rule.rule} - Methods: {rule.methods}')
            
    except Exception as e:
        app.logger.error(f'Failed to register API blueprint: {str(e)}', exc_info=True)
        raise  # Re-raise the exception to see the full traceback
    
    @app.route('/')
    async def index():
        return render_template('index.html')

    @app.before_request
    async def before_request():
        g.request_start_time = time.time()

    @app.after_request
    async def after_request(response):
        if hasattr(g, 'request_start_time'):
            elapsed = time.time() - g.request_start_time
            response.headers['X-Request-Time'] = str(elapsed)
        return response

    @app.errorhandler(500)
    async def internal_error(error):
        app.logger.error('Server Error: %s', error)
        return render_template('errors/500.html'), 500

    @app.errorhandler(404)
    async def not_found_error(error):
        app.logger.error('Not Found Page 404 Error: %s', error)
        return render_template('errors/404.html'), 404

    return app

# Create the ASGI application
asgi_app = create_app() 