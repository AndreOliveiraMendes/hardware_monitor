from flask import Blueprint, render_template, request

from app.db import get_latest_metrics, get_metrics, get_names, get_types

bp = Blueprint('visualization', __name__, url_prefix='/visualization')

@bp.route('/')
def index():
    return render_template('visualization/index.html')

@bp.route("/latest")
def latest():
    data = get_latest_metrics()
    return render_template('visualization/latest.html', data=data)

@bp.route("/dashboard")
def dashboard():
    start = request.args.get("start")
    end = request.args.get("end")
    tipo = request.args.get("type")
    name = request.args.get("name")
    data = get_metrics(start, end, tipo, name)
    types = get_types()
    names = get_names()
    return render_template("visualization/dashboard.html", data=data, types=types, names=names)