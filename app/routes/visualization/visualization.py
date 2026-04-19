from flask import Blueprint, render_template

from app.db import get_info_types, get_names, get_device_types_temperature

bp = Blueprint('visualization', __name__, url_prefix='/visualization')

@bp.route('/')
def index():
    return render_template('visualization/index.html')

@bp.route("/latest")
def latest():
    return render_template('visualization/latest.html')

@bp.route("/dashboard")
def dashboard():
    info_types = get_info_types()
    device_types = get_device_types_temperature()
    names = get_names()
    return render_template("visualization/dashboard.html", info_types=info_types, device_types=device_types, names=names)