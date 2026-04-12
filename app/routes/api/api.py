from flask import Blueprint, jsonify, render_template, request, url_for

from app.db import get_latest_metrics

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route("/")
def menu():
    info = {
            "name": "Monitor API",
            "version": "1.0",
            "endpoints": [
                {
                    "path": url_for('api.metrics'),
                    "method": "GET",
                    "description": "Get latest metrics"
                }
            ]
    }
    if "application/json" in request.headers.get("Accept", ""):
        return jsonify(info)
    else:
        return render_template("api/menu.html", info=info)

@bp.route("/latest")
def metrics():
    return jsonify(get_latest_metrics())