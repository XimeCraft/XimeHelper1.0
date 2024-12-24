from flask import Flask, render_template
import os
from dotenv import load_dotenv
from .logger import setup_logger
from .config import Config

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
    setup_logger(app)
    app.logger.info('Starting XimeHelper application...')
    
    # Register blueprints
    try:
        from AutoFileManagement.AutoFileOpening.api.routes import bp as file_bp
        app.register_blueprint(file_bp, url_prefix='/api')
        app.logger.info('Registered API blueprint successfully')
    except Exception as e:
        app.logger.error(f'Failed to register API blueprint: {str(e)}')
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
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
    app.run(debug=True, host='127.0.0.1', port=5000) 