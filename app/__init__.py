from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from app.extension import init_db
from app.helpers.helpers import templater_helpers
from app.routes import register_blueprints
from config_loging import setup_logging

def create_app():
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_prefix=1)

    init_db()

    setup_logging(app)
    
    with app.app_context():
        templater_helpers(app)
        
        register_blueprints(app)
        
    app.logger.info("started")

    return app
