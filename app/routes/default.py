from flask import Blueprint, render_template

from app.db import get_latest_metrics


bp = Blueprint('default', __name__)

@bp.route('/')
def index():
    data = get_latest_metrics()
    return render_template('index.html', data=data)