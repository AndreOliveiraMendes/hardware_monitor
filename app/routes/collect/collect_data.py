from flask import Blueprint, jsonify, request

from app.db import insert_metric


bp = Blueprint('collect', __name__)

@bp.route("/ingest", methods=["POST"])
def ingest():
    data = request.get_json()

    if isinstance(data, dict):
        data = [data]

    for item in data:
        insert_metric(item["type"], item["hostname"], item["hostip"],item["name"], item["value"])

    return jsonify({"status": "ok"})