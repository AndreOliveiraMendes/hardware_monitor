from flask import Blueprint, render_template

from app.db import get_names, get_types

bp = Blueprint('visualization', __name__, url_prefix='/visualization')

@bp.route('/')
def index():
    return render_template('visualization/index.html')

@bp.route("/latest")
def latest():
    return render_template('visualization/latest.html')

@bp.route("/dashboard")
def dashboard():
    types = get_types()
    names = get_names()
    return render_template("visualization/dashboard.html", types=types, names=names)