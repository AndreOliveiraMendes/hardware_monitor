from flask import Blueprint, json, jsonify, request

from app.routes.collect.handler import collect_data

bp = Blueprint('collect', __name__)

@bp.route("/ingest", methods=["POST"])
def ingest():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"status": "error", "message": "invalid or empty JSON"}), 400

    if isinstance(data, dict):
        data = [data]

    if not isinstance(data, list):
        return jsonify({"status": "error", "message": "payload must be dict or list"}), 400

    success = 0
    errors = 0
    messages = []

    for item in data:
        if not isinstance(item, dict):
            errors += 1
            messages.append("item is not a dict")
            continue

        # normaliza meta
        if isinstance(item.get("meta"), dict):
            item["meta"] = json.dumps(item["meta"])

        try:
            code, msg = collect_data(item)
        except Exception as e:
            errors += 1
            messages.append(str(e))
            continue

        if code != 200:
            errors += 1
            messages.append(msg)
        else:
            success += 1

    response = {
        "status": "ok" if success > 0 else "error",
        "success": success,
        "errors": errors,
    }

    if messages:
        response["messages"] = messages

    # 👇 status mais honesto
    if success > 0 and errors > 0:
        return jsonify(response), 207  # Multi-Status (parcial)
    elif success > 0:
        return jsonify(response), 200
    else:
        return jsonify(response), 400