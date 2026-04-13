from flask import Blueprint, jsonify, request

from app.routes.collect.handler import collect_data

bp = Blueprint('collect', __name__)

@bp.route("/ingest", methods=["POST"])
def ingest():
    data = request.get_json()

    if isinstance(data, dict):
        data = [data]

    for item in data:
        code, msg = collect_data(item)
        if code != 200:
            return jsonify({"error": msg}), code

    return jsonify({"status": "ok"})