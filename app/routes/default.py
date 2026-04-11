from flask import Blueprint, jsonify, render_template

from app.db import get_latest_metrics


bp = Blueprint('default', __name__)

@bp.route('/')
def index():
    data = get_latest_metrics()
    return render_template('index.html', data=data)

@bp.route("/json")
def metrics():
    return jsonify(get_latest_metrics())