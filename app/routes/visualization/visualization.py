from flask import Blueprint, jsonify, render_template

from app.db import get_latest_metrics
from app.extension import get_conn


bp = Blueprint('visualization', __name__, url_prefix='/visualization')

@bp.route("/dashboard")
def dashboard():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT datetime(timestamp, 'localtime'), type, name, value
        FROM metrics
        ORDER BY timestamp DESC
        LIMIT 100
    """)

    rows = cur.fetchall()
    conn.close()

    return render_template("dashboard.html", rows=rows)


@bp.route("/metrics")
def metrics():
    return jsonify(get_latest_metrics())