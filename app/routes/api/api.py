from flask import Blueprint, jsonify, render_template, request, url_for

from app.db import get_latest_metrics, get_metrics

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route("/")
def menu():
    info = {
            "name": "Monitor API",
            "version": "1.0",
            "endpoints": [
                {
                    "path": url_for('api.last_metrics'),
                    "method": "GET",
                    "description": "Get latest metrics"
                },
                {
                    "path": url_for('api.all_metrics'),
                    "method": "GET",
                    "description": "Get all metrics acording to the aplied filters"
                }
            ]
    }
    if "application/json" in request.headers.get("Accept", ""):
        return jsonify(info)
    else:
        return render_template("api/menu.html", info=info)

@bp.route("/latest")
def last_metrics():
    return jsonify(get_latest_metrics())

@bp.route("/metrics")
def all_metrics():
    start = request.args.get("start")
    end = request.args.get("end")
    tipo = request.args.get("type")
    name = request.args.get("name")
    
    data = get_metrics(start, end, tipo, name)
    
    print(data)

    return jsonify(data)