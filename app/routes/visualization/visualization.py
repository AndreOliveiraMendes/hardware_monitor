from flask import Blueprint, render_template, request

from app.db import get_latest_metrics, get_metrics, get_types


bp = Blueprint('visualization', __name__, url_prefix='/visualization')

@bp.route("/dashboard")
def dashboard():
    start = request.args.get("start")
    end = request.args.get("end")
    tipo = request.args.get("type")
    data = get_metrics(start, end, tipo)
    types = get_types()
    return render_template("dashboard.html", data=data, types=types)