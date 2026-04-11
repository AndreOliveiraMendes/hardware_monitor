from flask import Flask

from app.extension import init_db
from app.helpers.helpers import templater_helpers
from app.routes import register_blueprints
from werkzeug.middleware.proxy_fix import ProxyFix

def create_app():
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_prefix=1)

    init_db()
    
    with app.app_context():
        templater_helpers(app)
        
        register_blueprints(app)

    return app
