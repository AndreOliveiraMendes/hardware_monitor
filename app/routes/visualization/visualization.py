from flask import Blueprint, render_template, request

from app.dao import get_daily_temperature_picks

bp = Blueprint('visualization', __name__, url_prefix='/visualization')

@bp.route('/')
def index():
    return render_template('visualization/index.html')

@bp.route("/latest")
def latest():
    return render_template('visualization/latest.html')

@bp.route("/dashboard")
def dashboard():
    return render_template("visualization/dashboard.html")

@bp.route("/grafico-temperatura")
def grafico_temperatura():
    device_type = request.args.get("device_type")
    name = request.args.get("name")
    selected = {
        "device_type": device_type,
        "name": name
    }
    return render_template("visualization/temperature.html",
        selected = selected
    )

@bp.route("/extremos")
def min_max_temp():
    device_type = request.args.get("device_type")
    name = request.args.get("name")

    try:
        page = int(request.args.get("page", 0))
    except:
        page = 0

    page = max(page, 0)

    result = get_daily_temperature_picks(device_type, name, page)

    return render_template(
        "visualization/minmax.html",
        data=result["data"],
        pagination=result,
        selected={
            "device_type": device_type,
            "name": name
        }
    )