from interface.app import app
import logging

if __name__ == '__main__':

    app.logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    app.logger.addHandler(console_handler)
    
    app.run(debug=True, host='0.0.0.0', port=5001) 