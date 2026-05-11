from flask import Blueprint, render_template, request

from app.routes.meta.handler import load_config, save_config

bp = Blueprint('meta', __name__, url_prefix='/meta')

@bp.route("/about")
def about():
    return render_template("meta/about.html")

@bp.route("/config", methods=["GET", "POST"])
def config():
    config = load_config()

    if request.method == "POST":
        for key in config.keys():
            if key in request.form:
                config[key] = int(request.form[key])

        save_config(config)  # você já tem essa função basicamente

    return render_template("meta/config.html", config=config)