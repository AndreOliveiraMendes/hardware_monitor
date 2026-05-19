from collections import defaultdict

from flask import Blueprint, render_template, request, url_for

from app.dao import get_daily_temperature_picks
from app.routes.meta.handler import load_config
from app.routes.visualization.handler import get_level
from config import TEMP_LEVELS
import requests

bp = Blueprint('visualization', __name__, url_prefix='/visualization')

@bp.route('/')
def index():
    return render_template('visualization/index.html')

@bp.route("/latest")
def latest():
    return render_template('visualization/latest.html')

@bp.route("/dashboard")
def dashboard():
    host_ip = request.args.get("host_ip")
    info_type = request.args.get("info_type")
    device_type = request.args.get("device_type")
    name = request.args.get("name")
    selected = {
        "host_ip": host_ip,
        "info_type": info_type,
        "device_type": device_type,
        "name": name
    }
    return render_template("visualization/dashboard.html",
        selected = selected
    )

@bp.route("/grafico-temperatura")
def grafico_temperatura():
    host_ip = request.args.get("host_ip")
    device_type = request.args.get("device_type")
    name = request.args.get("name")
    selected = {
        "host_ip": host_ip,
        "device_type": device_type,
        "name": name
    }
    
    return render_template("visualization/temperature.html",
        selected = selected,
        limits = TEMP_LEVELS
    )

@bp.route("/extremos")
def min_max_temp():
    host_ip = request.args.get("host_ip")
    device_type = request.args.get("device_type")
    name = request.args.get("name")
    config = load_config()
    per_page = int(config.get("minmax_pagination", 100))

    try:
        page = int(request.args.get("page", 0))
    except:
        page = 0

    page = max(page, 0)

    result = get_daily_temperature_picks(host_ip, device_type, name, page, per_page=per_page)

    return render_template(
        "visualization/minmax.html",
        data=result["data"],
        pagination=result,
        selected={
            "host_ip": host_ip,
            "device_type": device_type,
            "name": name
        }
    )
    
@bp.route("/scoreboard")
def scoreboard():
    data = requests.get(url_for('api.get_ahscore', _external=True)).json()

    hosts = defaultdict(lambda: {"CPU": [], "disk": []})

    for ip, tipo, nome, score, status, ts in data:
        item = {
            "nome": nome,
            "valor": max(0, min(score, 100)),  # normaliza 0–100
            "status": status,
            "ts": ts,
            "raw": score  # mantém original (ex: -1)
        }

        hosts[ip][tipo].append(item)

    # 🔥 ordena hosts pelo pior score
    def worst_score(host):
        valores = [
            i["valor"]
            for t in host.values()
            for i in t
            if i["raw"] >= 0
        ]
        return max(valores) if valores else -1

    hosts_sorted = dict(
        sorted(hosts.items(), key=lambda h: worst_score(h[1]), reverse=True)
    )

    return render_template("visualization/scoreboard.html", hosts=hosts_sorted)