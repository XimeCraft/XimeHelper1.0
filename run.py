from interface.app import asgi_app as app
import logging
import asyncio
from hypercorn.config import Config
from hypercorn.asyncio import serve

if __name__ == '__main__':
    # Setup logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger('hypercorn')
    logger.setLevel(logging.DEBUG)
    
    # Configure Hypercorn
    config = Config()
    config.bind = ["0.0.0.0:5001"]
    config.use_reloader = True
    
    # Run the server
    asyncio.run(serve(app, config)) 