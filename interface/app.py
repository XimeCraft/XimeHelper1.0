from flask import Flask, render_template, request, g
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
    def index():
        app.logger.warning('Test warning log message')
        app.logger.error('Test error log message')
        return render_template('index.html')
    
    @app.before_request
    def before_request():
        g.start_time = time.time()
        request.start_time = time.time()

    @app.after_request
    def after_request(response):
        return response

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Server Error: {error}')
        return 'Internal Server Error', 500

    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.warning(f'Page not found: {error}')
        return 'Not Found', 404
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 