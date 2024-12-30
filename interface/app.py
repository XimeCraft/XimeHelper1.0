from flask import Flask, render_template, request, g
import os
from dotenv import load_dotenv
from .logger import setup_logger
from .config import Config
from prometheus_client import make_wsgi_app, Counter, Histogram
from werkzeug.middleware.dispatcher import DispatcherMiddleware
import time
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

# Define Prometheus Metrics
API_DURATION = Histogram(
    'api_request_duration_seconds', 
    'Duration of API requests in seconds', 
    ['endpoint']
)
API_REQUESTS = Counter(
    'api_requests_total', 
    'Total number of API requests', 
    ['endpoint', 'status']
)

REQUEST_COUNT = Counter(
    'app_request_count', 'Application Request Count',
    ['method', 'endpoint', 'http_status']
)
REQUEST_LATENCY = Histogram(
    'app_request_latency_seconds',
    'Application Request Latency',
    ['method', 'endpoint']
)

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
        app.logger.warning('Test warning log message')
        app.logger.error('Test error log message')
        return render_template('index.html')
    
    @app.before_request
    def before_request():
        g.start_time = time.time()
        request.start_time = time.time()

    @app.after_request
    def after_request(response):
        if request.endpoint:  
            if hasattr(g, 'start_time'):
                duration = time.time() - g.start_time
                API_DURATION.labels(
                    endpoint=request.endpoint
                ).observe(duration)
            
            API_REQUESTS.labels(
                endpoint=request.endpoint,
                status=str(response.status_code)
            ).inc()
        
        request_latency = time.time() - request.start_time
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.endpoint or 'unknown',
            http_status=response.status_code
        ).inc()
        REQUEST_LATENCY.labels(
            method=request.method,
            endpoint=request.endpoint or 'unknown'
        ).observe(request_latency)
        
        return response

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Server Error: {error}')
        return 'Internal Server Error', 500

    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.warning(f'Page not found: {error}')
        return 'Not Found', 404
    
    # Add prometheus wsgi middleware
    app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
        '/metrics': make_wsgi_app()
    })
    
    @app.route('/metrics')
    def metrics():
        return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000) 