from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from .db import init_db

def create_app():
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_prefix=1)

    # registrar blueprints
    from .routes.web import web_bp
    from .routes.api import api_bp

    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp, url_prefix="/monitor")

    init_db()

    return app
