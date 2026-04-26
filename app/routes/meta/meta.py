from flask import Blueprint, render_template

bp = Blueprint('meta', __name__, url_prefix='/meta')

@bp.route("/about")
def about():
    return render_template("meta/about.html")