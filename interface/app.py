from flask import Flask, render_template
import os
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__,
                static_folder='static',
                template_folder='templates')
    
    # Register blueprints
    from AutoFileManagement.AutoFileOpening.api.routes import bp as file_bp
    app.register_blueprint(file_bp, url_prefix='/api')
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000) 